"""Request-scoped family context for parents with more than one child."""

from dataclasses import dataclass

from django.db.models import Q
from django.utils import timezone

from .models import ClassMembership, GuardianChildRelationship


@dataclass(frozen=True)
class ChildContext:
    """One child a guardian may currently view, together with their class."""

    student: object
    relationship: GuardianChildRelationship
    membership: ClassMembership | None
    tone: int

    @property
    def name(self):
        return self.student.first_name

    @property
    def school_class(self):
        return self.membership.school_class if self.membership else None

    @property
    def school_name(self):
        return self.school_class.school.name if self.school_class else "Noch keiner Klasse zugeordnet"

    @property
    def class_name(self):
        if not self.school_class:
            return ""
        return self.school_class.display_name or self.school_class.name


def available_child_contexts(user):
    """Return only verified, currently viewable parent-child relationships.

    The class membership is intentionally resolved independently for every child.
    This keeps siblings at different schools isolated while giving a guardian one
    account to switch between them.
    """

    if not getattr(user, "is_authenticated", False) or not hasattr(user, "person"):
        return []
    today = timezone.localdate()
    relationships = list(
        GuardianChildRelationship.objects.filter(
            guardian_person=user.person,
            status="verified",
            verified_at__isnull=False,
            may_view_student_profile=True,
            valid_from__lte=today,
        )
        .filter(Q(valid_until__isnull=True) | Q(valid_until__gte=today))
        .select_related("student_person")
        .order_by("student_person__first_name", "student_person__last_name")
    )
    memberships = (
        ClassMembership.objects.filter(
            person_id__in=[item.student_person_id for item in relationships],
            status="active",
            valid_from__lte=today,
            school_class__school_year__starts_on__lte=today,
            school_class__school_year__ends_on__gte=today,
        )
        .filter(Q(valid_until__isnull=True) | Q(valid_until__gte=today))
        .select_related("school_class__school")
        .order_by("school_class__school__name", "school_class__name")
    )
    memberships_by_person = {}
    for membership in memberships:
        memberships_by_person.setdefault(membership.person_id, membership)
    return [
        ChildContext(
            student=relationship.student_person,
            relationship=relationship,
            membership=memberships_by_person.get(relationship.student_person_id),
            tone=index % 5 + 1,
        )
        for index, relationship in enumerate(relationships)
    ]


def active_child_context(request):
    """Resolve the optional child selected for this browser session."""

    contexts = available_child_contexts(request.user)
    selected_id = request.session.get("active_child_person_id")
    selected = next((item for item in contexts if item.student.id == selected_id), None)
    return contexts, selected


def active_child_school_class(request):
    """Return the class explicitly selected by a parent, if any."""

    _contexts, selected = active_child_context(request)
    return selected.school_class if selected else None
