"""Sanitized reference: export a personal WebUntis timetable as CSV."""

import csv
import os
from datetime import date, timedelta

import webuntis


def required(name):
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def main():
    student_id = int(required("WEBUNTIS_STUDENT_ID"))
    start = date.today() - timedelta(days=date.today().weekday())
    end = start + timedelta(days=6)
    with webuntis.Session(
        server=required("WEBUNTIS_SERVER"),
        school=required("WEBUNTIS_SCHOOL"),
        username=required("WEBUNTIS_USERNAME"),
        password=required("WEBUNTIS_PASSWORD"),
        useragent="Klasse-5e-reference",
    ).login() as session:
        lessons = session.timetable(student=student_id, start=start, end=end)
    output = os.environ.get("WEBUNTIS_OUTPUT", "timetable.csv")
    with open(output, "w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["start", "end", "subject", "teacher", "room", "status"])
        for lesson in lessons:
            writer.writerow(
                [
                    lesson.start.isoformat(),
                    lesson.end.isoformat(),
                    ",".join(item.name for item in lesson.subjects),
                    ",".join(item.name for item in lesson.teachers),
                    ",".join(item.name for item in lesson.rooms),
                    lesson.code or "regular",
                ]
            )


if __name__ == "__main__":
    main()
