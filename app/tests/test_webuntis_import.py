from datetime import date

import pytest

from klasse5e.core.models import Person, UserAccount
from klasse5e.webuntis.extra_models import (
    WebUntisCalendarSubscription,
    WebUntisSubjectMapping,
    WebUntisTeacherMapping,
)
from klasse5e.webuntis.ical import build_calendar
from klasse5e.webuntis.importer import sync_timetable
from klasse5e.webuntis.models import WebUntisConnection


class FakeAdapter:
    def call_readonly(self, method, *args, **kwargs):
        assert method == "getTimetable"
        assert kwargs["id"] == 1234
        return [
            {
                "id": 77,
                "date": 20990105,
                "startTime": 800,
                "endTime": 845,
                "su": [{"name": "KU"}],
                "te": [{"name": "ABC"}],
                "ro": [{"name": "R1"}],
            }
        ]


@pytest.fixture
def connection(db):
    user = UserAccount.objects.create_user(
        email="webuntis@example.test", password="synthetic-password"
    )
    student = Person.objects.create(first_name="Test", last_name="Student")
    return WebUntisConnection.objects.create(
        user=user,
        student=student,
        external_student_id=1234,
        username_encrypted=b"synthetic",
        password_encrypted=b"synthetic",
    )


@pytest.mark.django_db
def test_timetable_is_mapped_and_idempotent(connection):
    WebUntisSubjectMapping.objects.create(code="KU", label="Kunst")
    WebUntisTeacherMapping.objects.create(code="ABC", label="Test Teacher")

    assert sync_timetable(connection, FakeAdapter(), today=date(2099, 1, 1)) == 1
    lesson = connection.lessons.get()
    assert lesson.subject == "Kunst"
    assert lesson.teacher_label == "Test Teacher"
    assert lesson.room == "R1"
    assert sync_timetable(connection, FakeAdapter(), today=date(2099, 1, 1)) == 0


@pytest.mark.django_db
def test_calendar_contains_mapped_lesson(connection, monkeypatch):
    WebUntisSubjectMapping.objects.create(code="KU", label="Kunst")
    WebUntisTeacherMapping.objects.create(code="ABC", label="Test Teacher")
    sync_timetable(connection, FakeAdapter(), today=date(2099, 1, 1))
    monkeypatch.setattr("klasse5e.webuntis.ical.timezone.now", lambda: connection.lessons.get().starts_at)
    calendar = build_calendar(connection)
    assert "SUMMARY:Kunst" in calendar
    assert "Lehrkraft: Test Teacher" in calendar
    assert calendar.endswith("END:VCALENDAR\r\n")


@pytest.mark.django_db
def test_calendar_token_is_hashed_and_rotatable(connection):
    subscription, token = WebUntisCalendarSubscription.issue(connection)
    assert token not in subscription.token_hash
    assert WebUntisCalendarSubscription.resolve(token) == subscription
    subscription.active = False
    subscription.save(update_fields=["active"])
    assert WebUntisCalendarSubscription.resolve(token) is None


class FakeHomeworkAdapter:
    def call_readonly(self, method, *args, **kwargs):
        assert method == "homework"
        assert kwargs["studentId"] == 1234
        return {
            "data": {
                "homeworks": [
                    {
                        "id": 91,
                        "lessonId": 77,
                        "date": "2099-01-02",
                        "dueDate": "2099-01-05",
                        "text": "Synthetic task",
                        "remark": "Bring notes",
                        "completed": False,
                    }
                ],
                "lessons": [{"id": 77, "subject": {"name": "KU", "longName": "Kunst"}}],
                "records": [],
                "teachers": [],
            }
        }


@pytest.mark.django_db
def test_parent_homework_payload_joins_lesson_subject(connection):
    from klasse5e.webuntis.importer import sync_homework

    WebUntisSubjectMapping.objects.create(code="KU", label="Kunst")
    assert sync_homework(connection, FakeHomeworkAdapter(), today=date(2099, 1, 1)) == 1
    homework = connection.homework.get()
    assert homework.subject == "Kunst"
    assert homework.assigned_on == date(2099, 1, 2)
    assert homework.due_on == date(2099, 1, 5)
    assert homework.text == "Synthetic task - Bring notes"
    assert homework.source_status == "open"


@pytest.mark.django_db
def test_numeric_ids_are_derived_from_private_reference_exports(connection, tmp_path):
    from klasse5e.webuntis.reference_mapping import apply_reference_mapping

    class NumericAdapter:
        def call_readonly(self, method, *args, **kwargs):
            return [
                {
                    "id": 88,
                    "date": 20990105,
                    "startTime": 800,
                    "endTime": 845,
                    "su": [{"id": 83}],
                    "te": [{"id": 86}],
                    "ro": [{"id": 47}],
                }
            ]

    sync_timetable(connection, NumericAdapter(), today=date(2099, 1, 1))
    timetable = tmp_path / "timetable.csv"
    timetable.write_text(
        "Wochentag;Datum;Von;Bis;Fach;Raum;Klasse;Status\n"
        "Montag;05.01.2099;08:00;08:45;KU;47;5e;regular\n",
        encoding="utf-8",
    )
    mappings = tmp_path / "class_mappings.csv"
    mappings.write_text(
        "subject_code,subject_label,teacher_code,teacher_label\n"
        "KU,Kunst,Duv,Test Teacher\n",
        encoding="utf-8",
    )

    result = apply_reference_mapping(
        connection,
        timetable_path=timetable,
        class_mapping_path=mappings,
    )
    lesson = connection.lessons.get()
    assert result == {"subject_aliases": 1, "teacher_aliases": 1, "changed_lessons": 1}
    assert lesson.subject == "Kunst"
    assert lesson.teacher_label == "Test Teacher"


@pytest.mark.django_db
def test_unified_calendar_has_colored_homework_and_lesson(connection, school_class):
    from klasse5e.core.calendar_presenter import build_calendar_context
    from klasse5e.itslearning.models import ItslearningConnection
    from klasse5e.webuntis.models import WebUntisHomework

    sync_timetable(connection, FakeAdapter(), today=date(2099, 1, 1))
    WebUntisHomework.objects.create(
        connection=connection,
        external_fingerprint="synthetic-homework",
        subject="Kunst",
        due_on=date(2099, 1, 5),
        text="Synthetic task",
    )
    context = build_calendar_context(
        school_class=school_class,
        selected_day=date(2099, 1, 5),
        webuntis_connections=WebUntisConnection.objects.filter(pk=connection.pk),
        itslearning_connections=ItslearningConnection.objects.none(),
    )
    kinds = {item["kind"] for item in context["agenda"]}
    assert {"lesson", "homework"}.issubset(kinds)
    assert len(context["calendar_days"]) == 42
