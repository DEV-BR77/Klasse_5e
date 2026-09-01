"""Sanitized reference: create a one-time iCalendar file."""

import os
from datetime import UTC, date, timedelta

import webuntis


def required(name):
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def escape(value):
    return str(value).replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")


def main():
    student_id = int(required("WEBUNTIS_STUDENT_ID"))
    start = date.today() - timedelta(days=date.today().weekday())
    end = start + timedelta(days=13)
    with webuntis.Session(
        server=required("WEBUNTIS_SERVER"),
        school=required("WEBUNTIS_SCHOOL"),
        username=required("WEBUNTIS_USERNAME"),
        password=required("WEBUNTIS_PASSWORD"),
        useragent="Klasse-5e-reference",
    ).login() as session:
        lessons = session.timetable(student=student_id, start=start, end=end)
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Klasse 5e//Reference//DE"]
    for lesson in lessons:
        subject = ", ".join(item.name for item in lesson.subjects) or "Unterricht"
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:webuntis-{lesson.id}@reference",
                f"DTSTART:{lesson.start.astimezone(UTC).strftime('%Y%m%dT%H%M%SZ')}",
                f"DTEND:{lesson.end.astimezone(UTC).strftime('%Y%m%dT%H%M%SZ')}",
                f"SUMMARY:{escape(subject)}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    output = os.environ.get("WEBUNTIS_OUTPUT", "timetable.ics")
    with open(output, "w", encoding="utf-8", newline="") as stream:
        stream.write("\r\n".join(lines) + "\r\n")


if __name__ == "__main__":
    main()
