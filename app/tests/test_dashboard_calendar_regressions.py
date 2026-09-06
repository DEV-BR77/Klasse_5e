from datetime import date, time

import pytest
from django.template.loader import render_to_string
from django.utils import translation

from klasse5e.core.ui_views import dashboard
from klasse5e.meals.models import MealDay, MealOption, MealPlan
from klasse5e.schedule.models import TimetableEntry


@pytest.mark.django_db
def test_calendar_css_positions_are_not_localized(client, guardian, school_class, year):
    for hour, subject in [(8, "Mathematik"), (10, "Sport"), (12, "Deutsch")]:
        TimetableEntry.objects.create(
            school_class=school_class, school_year=year, weekday=2,
            starts_at=time(hour), ends_at=time(hour, 45), subject=subject,
        )
    client.force_login(guardian)
    with translation.override("de"):
        response = client.get("/kalender/?tag=2026-09-08&ansicht=day", secure=True)
    import re
    html = response.content.decode()
    positions = re.findall(r"--item-top: ([^;]+);", html)
    assert len(positions) == 3
    assert len(set(positions)) == 3
    assert all("," not in value for value in positions)
    assert 'data-replace-history' in html


@pytest.mark.django_db
def test_dashboard_selected_day_and_weekly_meals(rf, guardian):
    plan = MealPlan.objects.create(
        source_id="synthetic-week", iso_year=2026, iso_week=37,
        starts_on=date(2026, 9, 7), ends_on=date(2026, 9, 11),
        status="ready", legend={"allergens": {"A": "Getreide"}, "additives": {"1": "Farbstoff"}},
    )
    for day, text in [(7, "Montagsmenü"), (8, "Dienstagsmenü")]:
        meal = MealDay.objects.create(plan=plan, date=date(2026, 9, day))
        MealOption.objects.create(day=meal, line=1, components=[text], allergen_codes=["A"], additive_codes=["1"])
    request = rf.get("/?tag=2026-09-08")
    request.user = guardian
    request.session = {}
    html = dashboard(request).content.decode()
    assert 'href="/?tag=2026-09-07"' in html
    assert 'href="/?tag=2026-09-08" aria-current="date"' in html
    assert "Tagesmenü · 08.09." in html
    day_panel = html.split('id="dashboard-panel-news"')[0]
    assert "Dienstagsmenü" in day_panel and "Montagsmenü" not in day_panel
    assert "Montagsmenü" in html and "Freitag, 11.09." in html
    all_weeks = render_to_string("meals/plans.html", {"plans": [plan]})
    assert "Allergen: Getreide" in all_weeks
    assert "Zusatzstoff: Farbstoff" in all_weeks
