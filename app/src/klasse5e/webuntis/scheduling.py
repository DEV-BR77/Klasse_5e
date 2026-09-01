from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.utils import timezone


def _parse_time(value):
    try:
        return datetime.strptime(value, "%H:%M").time()
    except (TypeError, ValueError) as exc:
        raise ValidationError("Uhrzeiten müssen HH:MM entsprechen.") from exc


def validate_schedule(schedule):
    if schedule.timezone_name != "Europe/Berlin":
        raise ValidationError("Synchronisationspläne verwenden Europe/Berlin.")
    if schedule.mode == schedule.Mode.INTERVAL:
        if schedule.times or not schedule.interval_minutes:
            raise ValidationError("Im Intervallmodus ist genau ein Intervall erforderlich.")
        if not 5 <= schedule.interval_minutes <= 24 * 60:
            raise ValidationError("Das Intervall muss zwischen 5 Minuten und 24 Stunden liegen.")
    elif schedule.mode == schedule.Mode.FIXED_TIMES:
        if schedule.interval_minutes is not None or not schedule.times:
            raise ValidationError("Im Uhrzeitmodus sind feste Uhrzeiten erforderlich.")
        parsed = [_parse_time(value) for value in schedule.times]
        if len(parsed) != len(set(parsed)) or len(parsed) > 12:
            raise ValidationError("Uhrzeiten müssen eindeutig und auf zwölf begrenzt sein.")
    else:
        raise ValidationError("Unbekannter Zeitplanmodus.")


def next_run(schedule, *, after=None):
    validate_schedule(schedule)
    after = after or timezone.now()
    if schedule.mode == schedule.Mode.INTERVAL:
        anchor = schedule.last_started_at or after
        candidate = anchor + timedelta(minutes=schedule.interval_minutes)
        return max(candidate, after)
    zone = ZoneInfo("Europe/Berlin")
    local_after = after.astimezone(zone)
    for day_offset in range(0, 8):
        day = local_after.date() + timedelta(days=day_offset)
        for clock in sorted(_parse_time(value) for value in schedule.times):
            candidate = datetime.combine(day, clock, tzinfo=zone)
            # Reject nonexistent wall times during the spring DST gap.
            if candidate.astimezone(ZoneInfo("UTC")).astimezone(zone).replace(fold=0) != candidate.replace(fold=0):
                continue
            if candidate > after:
                return candidate
    raise ValidationError("Kein nächster Lauf konnte bestimmt werden.")


TEMPORARY_ERRORS = {"temporary_network_error", "rate_limit", "browser_timeout", "browser_crashed"}
PERMANENT_ERRORS = {"invalid_credentials", "mfa_or_sso_required", "not_authorized", "invalid_response", "schema_error", "unsupported"}


def is_temporary_error(code):
    return code in TEMPORARY_ERRORS
