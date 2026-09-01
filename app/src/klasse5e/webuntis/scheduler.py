from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import SyncRun, SyncSchedule, WebUntisConnection
from .scheduling import next_run
from .sync import SyncThrottled, run_connection


@transaction.atomic
def claim_due_schedule(schedule_id, *, now=None):
    now = now or timezone.now()
    schedule = SyncSchedule.objects.select_for_update().get(pk=schedule_id)
    if not schedule.enabled or (schedule.next_run_at and schedule.next_run_at > now):
        return None
    if schedule.locked_until and schedule.locked_until > now:
        return None
    schedule.locked_until = now + timedelta(minutes=30)
    schedule.last_started_at = now
    schedule.next_run_at = next_run(schedule, after=now)
    schedule.save(update_fields=["locked_until", "last_started_at", "next_run_at"])
    return schedule


def run_due_schedules(*, now=None):
    now = now or timezone.now()
    results = []
    due_ids = SyncSchedule.objects.filter(enabled=True).filter(
        next_run_at__isnull=True
    ).values_list("pk", flat=True)
    due_ids = list(due_ids) + list(
        SyncSchedule.objects.filter(enabled=True, next_run_at__lte=now).values_list("pk", flat=True)
    )
    for schedule_id in dict.fromkeys(due_ids):
        schedule = claim_due_schedule(schedule_id, now=now)
        if not schedule or schedule.source != "webuntis":
            continue
        started = timezone.now()
        for connection in WebUntisConnection.objects.all().iterator():
            try:
                key = f"due:{schedule.pk}:{connection.pk}:{schedule.last_started_at.isoformat()}"
                results.append(run_connection(connection, trigger=SyncRun.Trigger.AUTOMATIC, idempotency_key=key))
            except SyncThrottled:
                continue
        finished = timezone.now()
        schedule.last_finished_at = finished
        schedule.last_duration_ms = max(0, int((finished - started).total_seconds() * 1000))
        schedule.last_status = "failed" if any(item.status == SyncRun.Status.FAILED for item in results) else "success"
        schedule.last_error_class = next((item.error_code for item in results if item.error_code), "")
        schedule.locked_until = None
        schedule.save(update_fields=["last_finished_at", "last_duration_ms", "last_status", "last_error_class", "locked_until"])
    return results
