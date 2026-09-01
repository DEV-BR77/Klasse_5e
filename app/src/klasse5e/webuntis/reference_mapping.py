import csv
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from django.db import transaction
from django.utils import timezone

from .extra_models import WebUntisSubjectMapping, WebUntisTeacherMapping
from .models import WebUntisLesson


def clean_label(value):
    return str(value or "").strip().rstrip(",").strip()


def _date(value):
    text = str(value or "").strip()
    for pattern in ("%Y-%m-%d", "%d.%m.%Y", "%Y%m%d"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue
    return None


def _clock(value):
    text = str(value or "").strip()
    for pattern in ("%H:%M", "%H.%M", "%H%M"):
        try:
            return datetime.strptime(text.zfill(4), pattern).time()
        except ValueError:
            continue
    return None


def _key(day, starts_at, ends_at, room):
    del room
    return day, starts_at.replace(second=0, microsecond=0), ends_at.replace(
        second=0, microsecond=0
    )


def _read_rows(path, *, delimiter=None):
    source = Path(path).resolve()
    if not source.is_file():
        raise FileNotFoundError(source.name)
    with source.open(encoding="utf-8-sig", newline="") as stream:
        if delimiter is None:
            sample = stream.read(4096)
            stream.seek(0)
            delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter
        yield from csv.DictReader(stream, delimiter=delimiter)


def load_class_mappings(path):
    mappings = {}
    for row in _read_rows(path):
        subject_code = clean_label(row.get("subject_code"))
        subject_label = clean_label(row.get("subject_label"))
        teacher_code = clean_label(row.get("teacher_code"))
        teacher_label = clean_label(row.get("teacher_label"))
        if subject_code and subject_label:
            mappings[subject_code] = {
                "subject_code": subject_code,
                "subject_label": subject_label,
                "teacher_code": teacher_code,
                "teacher_label": teacher_label,
            }
    return mappings


def load_reference_timetable(path):
    reference = defaultdict(set)
    for row in _read_rows(path, delimiter=";"):
        day = _date(row.get("Datum") or row.get("date"))
        starts_at = _clock(row.get("Von") or row.get("start"))
        ends_at = _clock(row.get("Bis") or row.get("end"))
        subject_code = clean_label(row.get("Fach") or row.get("subject"))
        if day and starts_at and ends_at and subject_code:
            reference[
                _key(day, starts_at, ends_at, row.get("Raum") or row.get("room"))
            ].add(subject_code)
    return reference


def _winner(votes):
    if not votes:
        return ""
    ordered = votes.most_common()
    if len(ordered) > 1 and ordered[0][1] == ordered[1][1]:
        return ""
    return ordered[0][0]


@transaction.atomic
def apply_reference_mapping(connection, *, timetable_path, class_mapping_path):
    class_mappings = load_class_mappings(class_mapping_path)
    class_lookup = {}
    for subject_code, mapping in class_mappings.items():
        class_lookup[subject_code.casefold()] = mapping
        class_lookup[mapping["subject_label"].casefold()] = mapping

    reference = load_reference_timetable(timetable_path)
    subject_votes = defaultdict(Counter)
    lessons = list(WebUntisLesson.objects.filter(connection=connection))
    for lesson in lessons:
        starts_at = timezone.localtime(lesson.starts_at)
        ends_at = timezone.localtime(lesson.ends_at)
        candidates = reference.get(
            _key(starts_at.date(), starts_at.time(), ends_at.time(), lesson.room), set()
        )
        if len(candidates) == 1 and lesson.subject_code:
            subject_votes[lesson.subject_code].update(candidates)

    numeric_subjects = {}
    for source_code, votes in subject_votes.items():
        reference_subject = _winner(votes)
        mapping = class_lookup.get(reference_subject.casefold()) if reference_subject else None
        if mapping:
            numeric_subjects[source_code] = mapping

    teacher_votes = defaultdict(Counter)
    for lesson in lessons:
        mapping = numeric_subjects.get(lesson.subject_code, {})
        teacher_label = mapping.get("teacher_label", "")
        if mapping and teacher_label and lesson.teacher_code:
            teacher_votes[lesson.teacher_code][teacher_label] += 1

    numeric_teachers = {
        source_code: teacher_label
        for source_code, votes in teacher_votes.items()
        if (teacher_label := _winner(votes))
    }

    for source_code, mapping in numeric_subjects.items():
        WebUntisSubjectMapping.objects.update_or_create(
            code=source_code,
            defaults={"label": mapping["subject_label"]},
        )
    for source_code, teacher_label in numeric_teachers.items():
        WebUntisTeacherMapping.objects.update_or_create(
            code=source_code,
            defaults={"label": teacher_label},
        )

    changed_lessons = 0
    subject_aliases = dict(WebUntisSubjectMapping.objects.values_list("code", "label"))
    teacher_aliases = dict(WebUntisTeacherMapping.objects.values_list("code", "label"))
    for lesson in lessons:
        subject = subject_aliases.get(lesson.subject_code, lesson.subject)
        teacher_label = teacher_aliases.get(lesson.teacher_code, lesson.teacher_label)
        updates = {}
        if subject and lesson.subject != subject:
            updates["subject"] = subject
        if teacher_label and lesson.teacher_label != teacher_label:
            updates["teacher_label"] = teacher_label
        if updates:
            WebUntisLesson.objects.filter(pk=lesson.pk).update(**updates)
            changed_lessons += 1

    return {
        "subject_aliases": len(numeric_subjects),
        "teacher_aliases": len(numeric_teachers),
        "changed_lessons": changed_lessons,
    }
