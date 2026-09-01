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
