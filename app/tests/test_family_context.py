from datetime import time, timedelta

import pytest
from django.utils import timezone

from klasse5e.core.models import (
    ClassMembership,
    GuardianChildRelationship,
    Person,
    School,
    SchoolClass,
)
from klasse5e.core.policies import has_active_membership
from klasse5e.schedule.models import CalendarEntry, TimetableEntry


@pytest.fixture
def two_school_family(guardian, school_class, year):
    other_school = School.objects.create(name="Heinrich-Nordhoff-Gesamtschule")
    other_class = SchoolClass.objects.create(
        school=other_school,
        school_year=year,
        name="7a",
        display_name="Jahrgang 7 · 7a",
    )
    mila = Person.objects.create(first_name="Mila", last_name="Beispiel")
    jonas = Person.objects.create(first_name="Jonas", last_name="Beispiel")
    for child, current_class in ((mila, school_class), (jonas, other_class)):
        ClassMembership.objects.create(
            person=child,
            school_class=current_class,
            valid_from=year.starts_on,
        )
        GuardianChildRelationship.objects.create(
            guardian_person=guardian.person,
            student_person=child,
            relationship_type="father",
            is_legal_guardian=True,
            may_view_student_profile=True,
            valid_from=year.starts_on,
            status="verified",
            verified_by=guardian,
            verified_at=timezone.now(),
        )
    starts_at = timezone.now() + timedelta(days=1)
    CalendarEntry.objects.create(
        school_class=school_class,
        school_year=year,
        kind="cancellation",
        title="Sport fällt aus",
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=1),
    )
    CalendarEntry.objects.create(
        school_class=other_class,
        school_year=year,
        kind="event",
        title="Elterninformation Jahrgang 7",
        starts_at=starts_at + timedelta(hours=2),
        ends_at=starts_at + timedelta(hours=3),
    )
    TimetableEntry.objects.create(
        school_class=school_class,
        school_year=year,
        weekday=1,
        starts_at=time(8),
        ends_at=time(8, 45),
        subject="Deutsch",
    )
    TimetableEntry.objects.create(
        school_class=other_class,
        school_year=year,
        weekday=1,
        starts_at=time(8),
        ends_at=time(8, 45),
        subject="Biologie",
    )
    return mila, jonas, other_class


@pytest.mark.django_db
def test_dashboard_combines_important_items_for_all_children(client, guardian, two_school_family):
    client.force_login(guardian)

    response = client.get("/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "Familie im Blick" in html
    assert "Mila" in html and "Jonas" in html
    assert "Sport fällt aus" in html
    assert "Elterninformation Jahrgang 7" in html


@pytest.mark.django_db
def test_parent_can_switch_the_class_area_to_one_child(client, guardian, two_school_family):
    mila, jonas, other_class = two_school_family
    client.force_login(guardian)

    response = client.get(f"/familie/ansicht/{jonas.id}/?next=/kalender/")

    assert response.status_code == 302
    assert response["Location"] == "/kalender/"
    assert client.session["active_child_person_id"] == jonas.id
    calendar = client.get("/kalender/?tag=2026-09-07&ansicht=day")
    assert calendar.status_code == 200
    assert calendar.context["calendar_child"].student == jonas
    assert calendar.context["membership"].school_class == other_class
    assert "Biologie" in calendar.content.decode()
    assert "Deutsch" not in calendar.content.decode()

    response = client.get(f"/familie/ansicht/{mila.id}/?next=/")
    assert response.status_code == 302
    assert client.session["active_child_person_id"] == mila.id


@pytest.mark.django_db
def test_parent_cannot_select_an_unrelated_child(client, guardian, two_school_family):
    outsider = Person.objects.create(first_name="Unbekannt", last_name="Kind")
    client.force_login(guardian)

    response = client.get(f"/familie/ansicht/{outsider.id}/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_verified_parent_has_access_only_to_their_childs_active_class(
    guardian, two_school_family
):
    _mila, _jonas, other_class = two_school_family

    assert has_active_membership(guardian, other_class)
