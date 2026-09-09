from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from klasse5e.webuntis.absence_verification import AbsenceRecord, verified_new_absence


@pytest.fixture
def expected():
    start = datetime(2026, 9, 10, 6, tzinfo=UTC)
    return AbsenceRecord("synthetic-child", start, start + timedelta(hours=6), "Test")


def test_only_new_exact_record_confirms(expected):
    fresh = replace(expected, external_id="new")
    assert verified_new_absence(expected, [], [fresh]) == fresh
    assert verified_new_absence(expected, [fresh], [fresh]) is None


@pytest.mark.parametrize("field,value", [("student_key", "sibling"), ("note", "Other")])
def test_wrong_child_or_content_never_confirms(expected, field, value):
    assert verified_new_absence(expected, [], [replace(expected, **{field: value})]) is None


def test_wrong_interval_and_missing_record(expected):
    wrong = replace(expected, ends_at=expected.ends_at + timedelta(minutes=1))
    assert verified_new_absence(expected, [], [wrong]) is None
    assert verified_new_absence(expected, [], []) is None


def test_reused_identifier_is_not_a_new_submission(expected):
    previous = replace(expected, note="Previous", external_id="existing")
    changed = replace(expected, external_id="existing")
    assert verified_new_absence(expected, [previous], [changed]) is None


def test_unidentified_duplicates_and_multiple_new_matches_are_ambiguous(expected):
    assert verified_new_absence(expected, [expected], [expected, expected]) is None
    assert verified_new_absence(expected, [], [expected, expected]) is None
    assert verified_new_absence(expected, [], [expected]) == expected
