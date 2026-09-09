from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest

from klasse5e.webuntis.absence_submission import SubmissionOutcome, submit_once
from klasse5e.webuntis.absence_verification import AbsenceRecord


@pytest.fixture
def expected():
    start = datetime(2026, 9, 10, 6, tzinfo=UTC)
    return AbsenceRecord("synthetic", start, start + timedelta(hours=1), "", "new")


def test_delayed_read_is_confirmed_without_repeating_write(expected):
    browser = Mock()
    browser.read_absences.side_effect = [[], [], [expected]]
    assert submit_once(browser, expected, authorize=Mock()) == SubmissionOutcome.CONFIRMED
    browser.submit_absence.assert_called_once_with()


def test_timeout_after_acceptance_can_be_confirmed(expected):
    browser = Mock()
    browser.submit_absence.side_effect = TimeoutError
    browser.read_absences.side_effect = [[], [expected]]
    assert submit_once(browser, expected, authorize=Mock()) == SubmissionOutcome.CONFIRMED
    browser.submit_absence.assert_called_once_with()


def test_unconfirmed_write_has_bounded_reads(expected):
    browser = Mock()
    browser.read_absences.return_value = []
    browser.submit_absence.side_effect = TimeoutError
    assert submit_once(browser, expected, authorize=Mock()) == SubmissionOutcome.UNCONFIRMED
    assert browser.read_absences.call_count == 4
    browser.submit_absence.assert_called_once_with()


def test_revoked_authorization_prevents_write(expected):
    browser = Mock()
    browser.read_absences.return_value = []
    authorize = Mock(side_effect=[None, PermissionError])
    assert submit_once(browser, expected, authorize=authorize) == SubmissionOutcome.NOT_SENT
    browser.submit_absence.assert_not_called()


def test_failed_baseline_never_writes(expected):
    browser = Mock()
    browser.read_absences.side_effect = TimeoutError
    assert submit_once(browser, expected, authorize=Mock()) == SubmissionOutcome.NOT_SENT
    browser.submit_absence.assert_not_called()


def test_revocation_after_write_stops_further_access(expected):
    browser = Mock()
    browser.read_absences.return_value = []
    authorize = Mock(side_effect=[None, None, PermissionError])
    assert submit_once(browser, expected, authorize=authorize) == SubmissionOutcome.UNCONFIRMED
    assert browser.read_absences.call_count == 1
