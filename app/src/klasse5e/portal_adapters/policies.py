"""Server-side access checks for school-approved portal adapters.

The catalogue controls what a school may offer.  A ``ChildModuleConnection``
is the additional, personal opt-in for one child.  Both conditions are needed
before concrete adapters may persist credentials or retrieve school data.
"""

from django.db.models import Exists, OuterRef, Q
from django.utils import timezone

from klasse5e.core.models import ClassMembership

from .models import ChildModuleConnection, PortalAdapterModule


def active_membership(student):
    """Return the student's currently valid class membership, if any."""

    today = timezone.localdate()
    return (
        ClassMembership.objects.filter(
            person=student,
            status="active",
            valid_from__lte=today,
        )
        .filter(Q(valid_until__isnull=True) | Q(valid_until__gte=today))
        .select_related("school_class", "school_class__school")
        .order_by("school_class__school_year__starts_on", "id")
        .last()
    )


def school_modules(student, provider):
    """Return modules enabled for the child's active school and class."""

    membership = active_membership(student)
    if membership is None:
        return PortalAdapterModule.objects.none()
    class_links = PortalAdapterModule.available_to_classes.through.objects.filter(
        portaladaptermodule_id=OuterRef("pk")
    )
    return (
        PortalAdapterModule.objects.filter(
            adapter__provider=provider,
            adapter__is_enabled=True,
            is_enabled=True,
        )
        .filter(
            Q(adapter__schools=membership.school_class.school)
            | Q(adapter__school=membership.school_class.school)
        )
        .filter(Q(available_to_classes=membership.school_class) | ~Exists(class_links))
        .select_related("adapter")
        .distinct()
    )


def personal_modules(student, provider):
    """Return school-approved modules personally enabled for ``student``."""

    return school_modules(student, provider).filter(
        child_connections__student=student,
        child_connections__is_enabled=True,
    )


def provider_available_for_student(student, provider):
    return personal_modules(student, provider).exists()


def set_connection_state(student, provider, state):
    """Reflect a credential change without storing credentials in the catalogue."""

    ChildModuleConnection.objects.filter(
        student=student,
        module__in=personal_modules(student, provider),
        module__requires_child_credentials=True,
    ).update(connection_state=state)
