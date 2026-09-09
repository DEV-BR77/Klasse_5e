"""Transport-independent verification of a newly submitted browser absence.

Callers supply a fresh browser read and a snapshot taken before submission.
Neither a successful click nor a pre-existing matching record confirms a write.
This module deliberately performs no network access and never retries writes.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AbsenceRecord:
    student_key: str
    starts_at: datetime
    ends_at: datetime
    note: str
    external_id: str = ""

    def __post_init__(self):
        if not self.student_key.strip() or self.ends_at <= self.starts_at:
            raise ValueError("Invalid absence binding or interval")


def verified_new_absence(expected, before, after):
    """Return the sole new exact match, otherwise leave the outcome unconfirmed.

    Without source identifiers an identical baseline record is ambiguous, even
    when its count increases. Changed records with reused IDs are not new writes.
    Dates retain their time zones; no lossy date-only matching is performed.
    """
    before = tuple(before)
    after = tuple(after)

    def matches(record):
        return (
            record.student_key == expected.student_key
            and record.starts_at == expected.starts_at
            and record.ends_at == expected.ends_at
            and record.note == expected.note
        )

    known_ids = {record.external_id for record in before if record.external_id}
    candidates = [
        record for record in after
        if matches(record)
        and (
            record.external_id not in known_ids
            if record.external_id
            else not any(matches(previous) for previous in before)
        )
    ]
    return candidates[0] if len(candidates) == 1 else None
