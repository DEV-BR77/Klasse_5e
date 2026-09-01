from datetime import date, time

import pytest
from django.utils import timezone

from klasse5e.core.models import (
    ClassMembership,
    Person,
    RoleAssignment,
    School,
    SchoolClass,
    SchoolYear,
    UserAccount,
)
from klasse5e.schedule.models import CalendarEntry, TimetableEntry
from klasse5e.schedule.services import update_calendar_entry


@pytest.fixture
def schedule_data(db):
    year = SchoolYear.objects.create(
        label="2026/27", starts_on=date(2026, 8, 1), ends_on=date(2027, 7, 31)
    )
    school = School.objects.create(name="Testschule", slug="schedule-testschule")
    school_class = SchoolClass.objects.create(
        school=school, name="Test 5e", code="5e", school_year=year
    )
    user = UserAccount.objects.create_user("calendar@example.test", "Test-Passwort-123!")
    person = Person.objects.create(user=user, first_name="Kal", last_name="Test")
    ClassMembership.objects.create(
        person=person, school_class=school_class, valid_from=date(2026, 8, 1)
    )
    TimetableEntry.objects.create(
        school_class=school_class,
        school_year=year,
        weekday=1,
        starts_at=time(8),
        ends_at=time(8, 45),
        subject="Mathematik",
    )
    now = timezone.now()
    entry = CalendarEntry.objects.create(
        school_class=school_class,
        school_year=year,
        kind="exam",
        title="Test",
        starts_at=now,
        ends_at=now + timezone.timedelta(hours=1),
    )
    return school_class, user, entry


@pytest.mark.django_db
def test_week_is_class_protected(client, schedule_data):
    school_class, user, _ = schedule_data
    client.force_login(user)
    response = client.get(f"/schedule/classes/{school_class.id}/week/")
    assert response.status_code == 200 and response.json()["lessons"][0]["subject"] == "Mathematik"
    stranger = UserAccount.objects.create_user(
        "stranger-calendar@example.test", "Test-Passwort-123!"
    )
    Person.objects.create(user=stranger, first_name="Fremd", last_name="Test")
    client.force_login(stranger)
    assert client.get(f"/schedule/classes/{school_class.id}/week/").status_code == 404


@pytest.mark.django_db
def test_change_detection_is_revisioned_and_noop_deduplicated(schedule_data):
    school_class, user, entry = schedule_data
    RoleAssignment.objects.create(user=user, school_class=school_class, role="editor")
    entry, changed = update_calendar_entry(entry, user, title="Neu")
    assert changed and entry.revision == 2 and entry.changes.count() == 1
    entry, changed = update_calendar_entry(entry, user, title="Neu")
    assert not changed and entry.changes.count() == 1


@pytest.mark.django_db
def test_ical_token_is_opaque_rotated_and_membership_bound(client, schedule_data):
    school_class, user, _ = schedule_data
    client.force_login(user)
    first = client.post(f"/schedule/classes/{school_class.id}/ical-token/").json()["url"]
    assert "calendar@example" not in first
    assert client.get(first).status_code == 200
    second = client.post(f"/schedule/classes/{school_class.id}/ical-token/").json()["url"]
    assert (
        first != second
        and client.get(first).status_code == 404
        and client.get(second).status_code == 200
    )
    membership = user.person.classmembership_set.get()
    membership.status = "ended"
    membership.save()
    assert client.get(second).status_code == 404
