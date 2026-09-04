from datetime import date, datetime, time

import pytest
from django.utils import timezone

from klasse5e.core.calendar_presenter import build_calendar_context
from klasse5e.core.models import Person
from klasse5e.itslearning.models import ItslearningConnection
from klasse5e.schedule.models import LessonPeriod, TimeGrid, TimetableEntry
from klasse5e.webuntis.models import WebUntisConnection, WebUntisLesson


@pytest.mark.django_db
def test_week_view_uses_school_periods_and_merges_double_lesson(school, school_class, year):
    grid = TimeGrid.objects.create(school=school, name="Regelplan", valid_from=date(2026, 8, 1))
    LessonPeriod.objects.create(time_grid=grid, number=1, starts_at=time(8), ends_at=time(8, 45))
    LessonPeriod.objects.create(
        time_grid=grid, number=2, starts_at=time(8, 50), ends_at=time(9, 35)
    )
    for starts_at, ends_at in ((time(8), time(8, 45)), (time(8, 50), time(9, 35))):
        TimetableEntry.objects.create(
            school_class=school_class,
            school_year=year,
            weekday=3,
            starts_at=starts_at,
            ends_at=ends_at,
            subject="Mathematik",
            teacher_label="Frau Beispiel",
        )

    context = build_calendar_context(
        school_class=school_class,
        selected_day=date(2026, 9, 2),
        webuntis_connections=WebUntisConnection.objects.none(),
        itslearning_connections=ItslearningConnection.objects.none(),
        view="week",
    )

    wednesday = context["timeline_days"][2]
    assert len(wednesday["items"]) == 1
    assert wednesday["items"][0]["is_double"] is True
    assert wednesday["items"][0]["duration_minutes"] == 95
    assert [period["duration"] for period in context["timeline_periods"]] == [45, 45]


@pytest.mark.django_db
def test_calendar_filters_and_view_switch_are_rendered(client, guardian, school_class, year):
    TimetableEntry.objects.create(
        school_class=school_class,
        school_year=year,
        weekday=3,
        starts_at=time(8),
        ends_at=time(8, 45),
        subject="Mathematik",
    )
    client.force_login(guardian)

    response = client.get(
        "/kalender/?tag=2026-09-02&ansicht=day&filter=1&kategorie=appointment",
        secure=True,
    )

    assert response.status_code == 200
    assert response.context["view"] == "day"
    assert response.context["agenda"] == []
    html = response.content.decode()
    assert "Monat" in html and "Woche" in html and "Tag" in html
    assert "Filter anwenden" in html
    assert "Mathematik" not in html


@pytest.mark.django_db
def test_day_view_builds_hourly_fallback_without_school_time_grid(guardian, school_class):
    student = Person.objects.create(first_name="Mila", last_name="Beispiel")
    connection = WebUntisConnection.objects.create(
        user=guardian,
        student=student,
        username_encrypted=b"x",
        password_encrypted=b"x",
    )
    zone = timezone.get_current_timezone()
    WebUntisLesson.objects.create(
        connection=connection,
        external_fingerprint="fallback-grid",
        subject="Deutsch",
        starts_at=timezone.make_aware(datetime(2026, 9, 4, 12, 20), zone),
        ends_at=timezone.make_aware(datetime(2026, 9, 4, 13, 5), zone),
    )

    context = build_calendar_context(
        school_class=school_class,
        selected_day=date(2026, 9, 4),
        webuntis_connections=WebUntisConnection.objects.filter(pk=connection.pk),
        itslearning_connections=ItslearningConnection.objects.none(),
        view="day",
    )

    assert context["timeline_uses_school_grid"] is False
    assert len(context["timeline_periods"]) >= 2
    assert all(period["label"].endswith("Uhr") for period in context["timeline_periods"])


@pytest.mark.django_db
def test_cancelled_original_is_hidden_when_replacement_uses_same_slot(guardian, school_class):
    student = Person.objects.create(first_name="Mila", last_name="Beispiel")
    connection = WebUntisConnection.objects.create(
        user=guardian,
        student=student,
        username_encrypted=b"x",
        password_encrypted=b"x",
    )
    zone = timezone.get_current_timezone()
    starts_at = timezone.make_aware(datetime(2026, 9, 4, 9, 40), zone)
    ends_at = timezone.make_aware(datetime(2026, 9, 4, 10, 25), zone)
    WebUntisLesson.objects.create(
        connection=connection,
        external_fingerprint="cancelled-original",
        subject="Mathematik",
        starts_at=starts_at,
        ends_at=ends_at,
        status="cancelled",
    )
    WebUntisLesson.objects.create(
        connection=connection,
        external_fingerprint="active-replacement",
        subject="Deutsch",
        starts_at=starts_at,
        ends_at=ends_at,
        status="irregular",
    )

    context = build_calendar_context(
        school_class=school_class,
        selected_day=date(2026, 9, 4),
        webuntis_connections=WebUntisConnection.objects.filter(pk=connection.pk),
        itslearning_connections=ItslearningConnection.objects.none(),
        view="day",
    )

    assert [item["title"] for item in context["agenda"]] == ["Deutsch"]
