"""One-shot submission orchestration; browser transport is injected.

The caller must durably claim an idempotency token and recheck authorization
before invoking this function. A transport must return fresh, child-bound reads.
Exceptions are intentionally reduced to neutral outcomes, never exposed as text.
"""

from enum import StrEnum

from .absence_verification import verified_new_absence


class SubmissionOutcome(StrEnum):
    CONFIRMED = "confirmed"
    NOT_SENT = "not_sent"
    UNCONFIRMED = "unconfirmed"


def submit_once(browser, expected, *, authorize, attempts=3):
    """Read baseline, authorize again, write once, and perform bounded fresh reads.

    The browser owns waiting for its page to finish loading. No write is retried,
    including when a click times out after the server may have accepted it.
    A timed-out write can still be confirmed by an independent fresh read.
    """
    if not 1 <= attempts <= 3:
        raise ValueError("Read attempts must be between one and three")
    try:
        authorize()
        before = tuple(browser.read_absences())
        browser.prepare_absence(expected)
        authorize()
    except Exception:
        return SubmissionOutcome.NOT_SENT

    try:
        browser.submit_absence()
    except Exception:
        # A timeout is not evidence that the school rejected the submission.
        pass

    for _ in range(attempts):
        try:
            authorize()
        except Exception:
            return SubmissionOutcome.UNCONFIRMED
        try:
            after = tuple(browser.read_absences())
            if verified_new_absence(expected, before, after) is not None:
                return SubmissionOutcome.CONFIRMED
        except Exception:
            continue
    return SubmissionOutcome.UNCONFIRMED
