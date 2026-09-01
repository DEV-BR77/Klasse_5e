import time
import uuid
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from klasse5e.core.models import ConsentType
from klasse5e.core.policies import consent_state

from .adapter import CAPABILITIES, WebUntisAdapter, classify_error
from .crypto import decrypt
from .importer import sync_feature
from .models import (
    FeatureState,
    SyncRun,
    SyncSchedule,
    WebUntisConnection,
    WebUntisFeaturePreference,
)
from .scheduling import is_temporary_error


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
    return SyncRun.objects.create(
        connection=connection, trigger=trigger, idempotency_key=key
    ), True


def _enabled_categories(connection):
    categories = []
    for key in connection.features.filter(enabled=True).values_list("key", flat=True):
        consent_type = ConsentType.objects.filter(key=f"webuntis_{key}").first()
        if consent_type and consent_state(consent_type, connection.student) == "allowed":
            categories.append(key)
    return categories


def _set_feature_state(connection, key, state):
    WebUntisFeaturePreference.objects.filter(connection=connection, key=key).update(
        state=state
    )


def _execute_once(run):
    categories = _enabled_categories(run.connection)
    total_changes = 0
    successes = 0
    first_error = ""
    imported_timetable = False
    try:
        adapter = WebUntisAdapter(
            server=run.connection.server,
            school=run.connection.school,
            username=decrypt(run.connection.username_encrypted),
            password=decrypt(run.connection.password_encrypted),
        )
        with adapter.client:
            for key in categories:
                if key in {"timetable_extended", "substitutions"} and imported_timetable:
                    _set_feature_state(run.connection, key, FeatureState.AVAILABLE)
                    continue
                try:
                    changes = sync_feature(run.connection, adapter, key)
                    if changes is None:
                        method = next(
                            (item.method for item in CAPABILITIES if item.key == key), None
                        )
                        if method:
                            adapter.call_readonly(method)
                    else:
                        total_changes += changes
                        imported_timetable = imported_timetable or key in {
                            "timetable",
                            "timetable_extended",
                            "substitutions",
                        }
                    successes += 1
                    _set_feature_state(run.connection, key, FeatureState.AVAILABLE)
                except Exception as exc:
                    code = classify_error(exc)
                    first_error = first_error or code
                    state = (
                        FeatureState.NOT_AUTHORIZED
                        if code == "not_authorized"
                        else FeatureState.UNSUPPORTED
                        if code in {"unsupported", "missing_student_id"}
                        else FeatureState.NOT_CHECKED
                    )
                    _set_feature_state(run.connection, key, state)
        if categories and not successes:
            run.status = SyncRun.Status.FAILED
        else:
            run.status = (
                SyncRun.Status.SUCCESS if total_changes else SyncRun.Status.NO_CHANGE
            )
            run.connection.last_successful_sync_at = timezone.now()
            run.connection.status = "ok"
            run.connection.save(
                update_fields=["last_successful_sync_at", "status", "updated_at"]
            )
    except Exception as exc:
        run.status = SyncRun.Status.FAILED
        first_error = first_error or classify_error(exc)
    run.categories = categories
    run.change_count = total_changes
    run.error_code = first_error[:40]
    run.finished_at = timezone.now()
    run.save(
        update_fields=[
            "status",
            "categories",
            "change_count",
            "error_code",
            "finished_at",
        ]
    )
    return run


def execute_run(run, *, sleep=time.sleep, notifier=None):
    """Execute one logical run at most three times for temporary failures."""
    for attempt in range(1, 4):
        run.attempt_count = attempt
        run.save(update_fields=["attempt_count"])
        run = _execute_once(run)
        if run.status != SyncRun.Status.FAILED or not is_temporary_error(run.error_code):
            return run
        if attempt < 3:
            sleep(0.25 * (2 ** (attempt - 1)))
            run.status = SyncRun.Status.RUNNING
            run.finished_at = None
            run.error_code = ""
            run.save(update_fields=["status", "finished_at", "error_code"])
    if run.status == SyncRun.Status.FAILED and run.attempt_count == 3:
        if notifier is None:
            from .notifications import notify_terminal_sync_failure

            notifier = notify_terminal_sync_failure
        notifier(run)
    return run


def run_connection(connection, *, trigger=SyncRun.Trigger.MANUAL, idempotency_key=None):
    run, created = begin_run(
        connection, trigger=trigger, idempotency_key=idempotency_key
    )
    return execute_run(run) if created else run
