from datetime import UTC, timedelta

from django.utils import timezone


def _escape(value):
    return (
        str(value or "")
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(",", "\\,")
        .replace(";", "\\;")
    )


def _stamp(value):
    return value.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def build_calendar(connection):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "PRODID:-//KlassID//Schuldaten//DE",
        "X-WR-CALNAME:KlassID Schule",
        "X-PUBLISHED-TTL:PT6H",
    ]
    start = timezone.now() - timedelta(days=14)
    end = timezone.now() + timedelta(days=180)
    for lesson in connection.lessons.filter(
        starts_at__gte=start, starts_at__lte=end
    ).order_by("starts_at"):
        title = lesson.subject or lesson.subject_code or "Unterricht"
        details = []
        if lesson.teacher_label:
            details.append(f"Lehrkraft: {lesson.teacher_label}")
        if lesson.room:
            details.append(f"Raum: {lesson.room}")
        if lesson.status != "regular":
            details.append(f"Status: {lesson.status}")
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:webuntis-lesson-{lesson.external_fingerprint}@klasse-5e",
                f"DTSTAMP:{_stamp(lesson.fetched_at)}",
                f"DTSTART:{_stamp(lesson.starts_at)}",
                f"DTEND:{_stamp(lesson.ends_at)}",
                f"SUMMARY:{_escape(title)}",
                f"DESCRIPTION:{_escape(chr(10).join(details))}",
                f"LOCATION:{_escape(lesson.room)}",
                "END:VEVENT",
            ]
        )
    for homework in connection.homework.filter(due_on__isnull=False).order_by("due_on"):
        if homework.due_on < timezone.localdate() - timedelta(days=14):
            continue
        if homework.due_on > timezone.localdate() + timedelta(days=180):
            continue
        next_day = homework.due_on + timedelta(days=1)
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:webuntis-homework-{homework.external_fingerprint}@klasse-5e",
                f"DTSTAMP:{_stamp(homework.fetched_at)}",
                f"DTSTART;VALUE=DATE:{homework.due_on.strftime('%Y%m%d')}",
                f"DTEND;VALUE=DATE:{next_day.strftime('%Y%m%d')}",
                f"SUMMARY:{_escape('Hausaufgabe ' + (homework.subject or ''))}",
                f"DESCRIPTION:{_escape(homework.text)}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
