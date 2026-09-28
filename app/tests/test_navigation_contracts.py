from pathlib import Path

import pytest
from django.test import RequestFactory
from django.urls import URLResolver, get_resolver, reverse

from klasse5e.core.navigation import parent_navigation


def _named_patterns(patterns):
    for pattern in patterns:
        if isinstance(pattern, URLResolver):
            yield from _named_patterns(pattern.url_patterns)
        elif pattern.name:
            yield pattern.name, str(pattern.pattern)


@pytest.mark.django_db
def test_class_detail_returns_to_its_school_class_tab(school_class):
    request = RequestFactory().get(reverse("school-class-detail", args=[school_class.pk]))

    parent = parent_navigation(request)

    assert parent == {
        "url": f"{reverse('school-detail', args=[school_class.school_id])}?tab=classes",
        "label": "Klassen der Schule",
    }


@pytest.mark.parametrize(
    ("path", "expected_url", "expected_label"),
    [
        ("/verwaltung/designsystem/", "/verwaltung/themes/", "Themes"),
        ("/verwaltung/adapter-definition/8/", "/verwaltung/adapter/", "Adapter"),
        ("/itslearning/speicher/", "/itslearning/", "itslearning"),
    ],
)
def test_specialist_pages_have_deterministic_parents(path, expected_url, expected_label):
    parent = parent_navigation(RequestFactory().get(path))

    assert parent == {"url": expected_url, "label": expected_label}


def test_schedule_routes_are_registered_once():
    named_patterns = list(_named_patterns(get_resolver().url_patterns))

    for route_name in ("schedule-week", "schedule-ical", "schedule-ical-issue"):
        assert [name for name, _path in named_patterns].count(route_name) == 1


def test_settings_directory_uses_collapsible_groups_instead_of_one_long_list():
    source = (
        Path(__file__).parents[1] / "templates" / "ui" / "more.html"
    ).read_text(encoding="utf-8")

    assert 'class="portal-directory__group"' in source
    assert 'class="portal-directory__section"' in source
    assert 'name="settings-area"' in source
    assert "<summary" in source
