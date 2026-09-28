from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from klasse5e.core.models import AuditEvent, Role
from klasse5e.core.module_permissions import may_manage_module

from .models import CalendarChange


def may_edit_schedule(user, school_class):
    return may_manage_module(
        user, "calendar", "edit", school_class, legacy_roles={Role.DEPUTY_ADMIN},
    )


@transaction.atomic
def update_calendar_entry(entry, user, **changes):
    if not may_edit_schedule(user, entry.school_class):
        raise PermissionDenied
    allowed = {"kind", "title", "starts_at", "ends_at", "room", "details"}
    changed = []
    for key, value in changes.items():
        if key in allowed and getattr(entry, key) != value:
            setattr(entry, key, value)
            changed.append(key)
    if not changed:
        return entry, False
    if entry.ends_at <= entry.starts_at:
        raise ValidationError("invalid_period")
    entry.revision += 1
    entry.save()
    CalendarChange.objects.create(
        entry=entry, revision=entry.revision, changed_fields=changed, changed_by=user
    )
    AuditEvent.objects.create(
        actor=user,
        action="calendar.entry.changed",
        target_type="calendar_entry",
        target_id=str(entry.id),
        metadata={"revision": entry.revision},
    )
    return entry, True
