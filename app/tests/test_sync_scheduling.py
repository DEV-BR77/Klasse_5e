from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError
from web_push_kit import DeliveryResult, DeliveryStatus

from klasse5e.core.models import (
    Person,
    PushPreference,
    PushSubscription,
    Role,
    RoleAssignment,
    UserAccount,
)
from klasse5e.webuntis.models import SyncRun, SyncSchedule, WebUntisConnection
from klasse5e.webuntis.notifications import notify_terminal_sync_failure
from klasse5e.webuntis.scheduling import next_run
from klasse5e.webuntis.sync import execute_run


def fixed_schedule(**values):
    defaults = {
        "source": "webuntis", "mode": SyncSchedule.Mode.FIXED_TIMES,
        "times": ["06:00", "12:00", "18:00"], "interval_minutes": None,
    }
    defaults.update(values)
    return SyncSchedule(**defaults)


def test_schedule_modes_do_not_contradict():
    fixed_schedule().clean()
    with pytest.raises(ValidationError):
        fixed_schedule(interval_minutes=60).clean()
    interval = fixed_schedule(mode=SyncSchedule.Mode.INTERVAL, times=[], interval_minutes=90)
    interval.clean()
    with pytest.raises(ValidationError):
        fixed_schedule(mode=SyncSchedule.Mode.INTERVAL, times=["06:00"], interval_minutes=90).clean()


def test_next_run_skips_nonexistent_dst_wall_time():
    schedule = fixed_schedule(times=["02:30"])
    after = datetime(2026, 3, 29, 0, 0, tzinfo=ZoneInfo("UTC"))
    result = next_run(schedule, after=after)
    assert result.date().isoformat() == "2026-03-30"
    assert result.strftime("%H:%M") == "02:30"


def test_winter_time_is_deterministic():
    schedule = fixed_schedule(times=["02:30"])
    after = datetime(2026, 10, 24, 23, 0, tzinfo=ZoneInfo("UTC"))
    result = next_run(schedule, after=after)
    assert result.astimezone(ZoneInfo("Europe/Berlin")).strftime("%Y-%m-%d %H:%M") == "2026-10-25 02:30"


@pytest.mark.django_db
def test_temporary_failure_retries_at_most_three(monkeypatch):
    user = UserAccount.objects.create_user("sync@example.test", "synthetic")
    student = Person.objects.create(first_name="Sync", last_name="Test")
    connection = WebUntisConnection.objects.create(
        user=user, student=student, username_encrypted=b"x", password_encrypted=b"x"
    )
    run = SyncRun.objects.create(connection=connection, trigger="automatic", idempotency_key="retry")
    calls = []

    def fail(item):
        calls.append(1)
        item.status = SyncRun.Status.FAILED
        item.error_code = "temporary_network_error"
        item.save(update_fields=["status", "error_code"])
        return item

    monkeypatch.setattr("klasse5e.webuntis.sync._execute_once", fail)
    execute_run(run, sleep=lambda _: None)
    run.refresh_from_db()
    assert len(calls) == 3
    assert run.attempt_count == 3


@pytest.mark.django_db
def test_permanent_failure_is_not_retried(monkeypatch):
    user = UserAccount.objects.create_user("permanent@example.test", "synthetic")
    student = Person.objects.create(first_name="Permanent", last_name="Test")
    connection = WebUntisConnection.objects.create(
        user=user, student=student, username_encrypted=b"x", password_encrypted=b"x"
    )
    run = SyncRun.objects.create(connection=connection, trigger="automatic", idempotency_key="permanent")
    calls = []

    def fail(item):
        calls.append(1)
        item.status = SyncRun.Status.FAILED
        item.error_code = "invalid_credentials"
        item.save(update_fields=["status", "error_code"])
        return item

    monkeypatch.setattr("klasse5e.webuntis.sync._execute_once", fail)
    execute_run(run, sleep=lambda _: None)
    assert len(calls) == 1


@pytest.mark.django_db
def test_terminal_failure_push_is_exactly_once():
    admin = UserAccount.objects.create_user("admin-sync@example.test", "synthetic")
    RoleAssignment.objects.create(user=admin, role=Role.PRIMARY_ADMIN)
    PushPreference.objects.create(user=admin, key="sync_errors", enabled=True)
    PushSubscription.from_values(admin, "https://push.example.test/id", "cHVia2V5", "YXV0aA")
    student = Person.objects.create(first_name="Push", last_name="Test")
    connection = WebUntisConnection.objects.create(
        user=admin, student=student, username_encrypted=b"x", password_encrypted=b"x"
    )
    run = SyncRun.objects.create(
        connection=connection, trigger="automatic", idempotency_key="push-once",
        status=SyncRun.Status.FAILED, attempt_count=3, error_code="temporary_network_error",
    )

    class Sender:
        def __init__(self):
            self.calls = 0

        def send(self, *_):
            self.calls += 1
            return DeliveryResult(DeliveryStatus.DELIVERED)

    sender = Sender()
    assert notify_terminal_sync_failure(run, sender=sender)
    assert not notify_terminal_sync_failure(run, sender=sender)
    assert sender.calls == 1
