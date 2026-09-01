import hashlib
from datetime import datetime, time, timedelta

from django.db import transaction
from django.utils import timezone

from .extra_models import WebUntisSubjectMapping, WebUntisTeacherMapping
from .homework_payload import homework_items
from .models import WebUntisHomework, WebUntisLesson


class MissingStudentId(Exception):
    code = "missing_student_id"


def _named(item, key):
    values = item.get(key) or []
    if isinstance(values, dict):
        values = [values]
    first = values[0] if values else {}
    if isinstance(first, str):
        return first, first
    code = str(first.get("name") or first.get("id") or "")
    label = str(first.get("longName") or first.get("displayName") or code)
    return code, label


def _lesson_datetime(day_value, clock_value):
    day_text = str(day_value)
    clock_text = str(clock_value).zfill(4)
    naive = datetime.combine(
        datetime.strptime(day_text, "%Y%m%d").date(),
        time(int(clock_text[:-2]), int(clock_text[-2:])),
    )
    return timezone.make_aware(naive, timezone.get_current_timezone())


def _date_value(value):
    if value in (None, ""):
        return None
    if isinstance(value, int) and value > 10_000_000_000:
        return datetime.fromtimestamp(value / 1000, tz=timezone.get_current_timezone()).date()
    text = str(value)[:10]
    for pattern in ("%Y-%m-%d", "%Y%m%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue
    return None


def _fingerprint(prefix, item, parts):
    external_id = item.get("id") or item.get("lessonId") or item.get("homeworkId")
    raw = f"{prefix}:{external_id or '|'.join(str(part) for part in parts)}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _changed(instance, defaults):
    return any(
        key != "delete_after" and getattr(instance, key) != value
        for key, value in defaults.items()
    )


@transaction.atomic
def sync_timetable(connection, adapter, *, today=None):
    if not connection.external_student_id:
        raise MissingStudentId()
    today = today or timezone.localdate()
    start = today - timedelta(days=7)
    end = today + timedelta(days=90)
    payload = adapter.call_readonly(
        "getTimetable",
        id=connection.external_student_id,
        type=5,
        startDate=int(start.strftime("%Y%m%d")),
        endDate=int(end.strftime("%Y%m%d")),
    )
    subject_map = dict(WebUntisSubjectMapping.objects.values_list("code", "label"))
    teacher_map = dict(WebUntisTeacherMapping.objects.values_list("code", "label"))
    seen = set()
    changes = 0
    for item in payload or []:
        if not isinstance(item, dict) or not item.get("date"):
            continue
        starts_at = _lesson_datetime(item["date"], item.get("startTime", 0))
        ends_at = _lesson_datetime(item["date"], item.get("endTime", 0))
        subject_code, source_subject = _named(item, "su")
        teacher_code, source_teacher = _named(item, "te")
        _room_code, room = _named(item, "ro")
        subject = subject_map.get(subject_code, source_subject or subject_code)
        teacher = teacher_map.get(teacher_code, source_teacher or teacher_code)
        fingerprint = _fingerprint(
            "lesson",
            item,
            (item.get("date"), item.get("startTime"), item.get("endTime"), subject_code),
        )
        defaults = {
            "starts_at": starts_at,
            "ends_at": ends_at,
            "subject_code": subject_code,
            "subject": subject,
            "teacher_code": teacher_code,
            "teacher_label": teacher,
            "room": room,
            "status": str(item.get("code") or "regular").lower(),
            "visibility": "personal",
            "delete_after": timezone.now() + timedelta(days=120),
        }
        existing = WebUntisLesson.objects.filter(
            connection=connection, external_fingerprint=fingerprint
        ).first()
        changed = existing is None or _changed(existing, defaults)
        WebUntisLesson.objects.update_or_create(
            connection=connection,
            external_fingerprint=fingerprint,
            defaults=defaults,
        )
        changes += int(changed)
        seen.add(fingerprint)
    stale = WebUntisLesson.objects.filter(
        connection=connection, starts_at__date__gte=start, starts_at__date__lte=end
    )
    if seen:
        stale = stale.exclude(external_fingerprint__in=seen)
    deleted, _ = stale.delete()
    return changes + deleted


def _homework_items(payload):
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    for key in ("homeworks", "data", "items", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            nested = _homework_items(value)
            if nested:
                return nested
    return []


@transaction.atomic
def sync_homework(connection, adapter, *, today=None):
    if not connection.external_student_id:
        raise MissingStudentId()
    today = today or timezone.localdate()
    payload = adapter.call_readonly(
        "homework",
        studentId=connection.external_student_id,
        startDate=(today - timedelta(days=14)).isoformat(),
        endDate=(today + timedelta(days=90)).isoformat(),
    )
    subject_map = dict(WebUntisSubjectMapping.objects.values_list("code", "label"))
    seen = set()
    changes = 0
    for item in homework_items(payload):
        if not isinstance(item, dict):
            continue
        subject_value = item.get("subject") or item.get("subjectName") or ""
        if isinstance(subject_value, dict):
            subject_code = str(subject_value.get("name") or subject_value.get("id") or "")
            source_subject = str(subject_value.get("longName") or subject_code)
        else:
            subject_code = str(subject_value)
            source_subject = subject_code
        text = str(
            item.get("text")
            or item.get("homework")
            or item.get("description")
            or item.get("remark")
            or ""
        ).strip()
        due_on = _date_value(item.get("dueDate") or item.get("due") or item.get("date"))
        assigned_on = _date_value(
            item.get("assignedDate") or item.get("startDate") or item.get("date")
        )
        fingerprint = _fingerprint(
            "homework", item, (subject_code, assigned_on, due_on, text)
        )
        defaults = {
            "subject": subject_map.get(subject_code, source_subject),
            "assigned_on": assigned_on,
            "due_on": due_on,
            "text": text,
            "source_status": str(item.get("status") or ""),
            "visibility": "personal",
            "delete_after": timezone.now() + timedelta(days=120),
        }
        existing = WebUntisHomework.objects.filter(
            connection=connection, external_fingerprint=fingerprint
        ).first()
        changed = existing is None or _changed(existing, defaults)
        WebUntisHomework.objects.update_or_create(
            connection=connection,
            external_fingerprint=fingerprint,
            defaults=defaults,
        )
        changes += int(changed)
        seen.add(fingerprint)
    return changes


def sync_feature(connection, adapter, key):
    if key in {"timetable", "timetable_extended", "substitutions"}:
        return sync_timetable(connection, adapter)
    if key == "homework":
        return sync_homework(connection, adapter)
    return None
