import uuid
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from klasse5e.core.models import ConsentType
from klasse5e.core.policies import consent_state

from .adapter import CAPABILITIES, WebUntisAdapter, classify_error
from .crypto import decrypt
from .models import SyncRun, SyncSchedule, WebUntisConnection


class SyncThrottled(Exception):
    pass


@transaction.atomic
def begin_run(connection, *, trigger, idempotency_key=None, minimum_minutes=None):
    connection = WebUntisConnection.objects.select_for_update().get(pk=connection.pk)
    latest = connection.sync_runs.order_by("-started_at").first()
    minimum = minimum_minutes or (
        10 if trigger == SyncRun.Trigger.MANUAL else SyncSchedule.current().min_interval_minutes
    )
    if (
        latest
        and latest.status == SyncRun.Status.RUNNING
        and latest.started_at > timezone.now() - timedelta(minutes=30)
    ):
        return latest, False
    if latest and latest.started_at > timezone.now() - timedelta(minutes=minimum):
        raise SyncThrottled()
    key = idempotency_key or uuid.uuid4().hex
    existing = SyncRun.objects.filter(idempotency_key=key).first()
    if existing:
        return existing, False
    return SyncRun.objects.create(connection=connection, trigger=trigger, idempotency_key=key), True


def execute_run(run):
    categories = []
    for key in run.connection.features.filter(enabled=True).values_list("key", flat=True):
        consent_type = ConsentType.objects.filter(key=f"webuntis_{key}").first()
        if consent_type and consent_state(consent_type, run.connection.student) == "allowed":
            categories.append(key)
    try:
        adapter = WebUntisAdapter(
            server=run.connection.server,
            school=run.connection.school,
            username=decrypt(run.connection.username_encrypted),
            password=decrypt(run.connection.password_encrypted),
        )
        with adapter.client:
            for key in categories:
                method = next((item.method for item in CAPABILITIES if item.key == key), None)
                if method:
                    adapter.call_readonly(method)
        run.status = SyncRun.Status.NO_CHANGE
        run.categories = categories
        run.connection.last_successful_sync_at = timezone.now()
        run.connection.status = "ok"
        run.connection.save(update_fields=["last_successful_sync_at", "status", "updated_at"])
    except Exception as exc:
        run.status = SyncRun.Status.FAILED
        run.error_code = classify_error(exc)[:40]
    run.finished_at = timezone.now()
    run.save(update_fields=["status", "categories", "error_code", "finished_at"])
    return run


def run_connection(connection, *, trigger=SyncRun.Trigger.MANUAL, idempotency_key=None):
    run, created = begin_run(connection, trigger=trigger, idempotency_key=idempotency_key)
    return execute_run(run) if created else run
