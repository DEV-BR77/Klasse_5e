from django.db import models
from django.utils import timezone

from .models import ClassMembership, GuardianChildRelationship, Role, RoleAssignment

PRIVILEGED_ROLES = {
    Role.PRIMARY_ADMIN,
    Role.DEPUTY_ADMIN,
    Role.TEACHER,
    Role.EDITOR,
    Role.MODERATOR,
    Role.ORGANIZER,
}


def active_roles(user, school_class=None):
    if not user.is_authenticated or not user.is_active or user.locked_at:
        return set()
    query = RoleAssignment.objects.filter(user=user, active=True)
    if school_class is not None:
        query = query.filter(school_class=school_class)
    return set(query.values_list("role", flat=True))


def has_active_membership(user, school_class):
    if (
        not user.is_authenticated
        or not user.is_active
        or user.locked_at
        or not hasattr(user, "person")
    ):
        return False
    today = timezone.localdate()
    return (
        ClassMembership.objects.filter(
            person=user.person,
            school_class=school_class,
            status="active",
            valid_from__lte=today,
            school_class__school_year__starts_on__lte=today,
            school_class__school_year__ends_on__gte=today,
        )
        .filter(models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=today))
        .exists()
    )


def may_view_student(user, student):
    if not hasattr(user, "person"):
        return False
    return any(
        rel.is_current() and rel.may_view_student_profile
        for rel in GuardianChildRelationship.objects.filter(
            guardian_person=user.person, student_person=student.person
        )
    )


def family_label(user):
    if not hasattr(user, "person"):
        return ""
    relation = (
        GuardianChildRelationship.objects.filter(guardian_person=user.person, status="verified")
        .select_related("student_person")
        .order_by("student_person__first_name")
        .first()
    )
    if not relation or not relation.is_current():
        return user.person.first_name
    relationship = relation.get_relationship_type_display()
    return f"{user.person.first_name} · {relationship} von {relation.student_person.first_name}"


def consent_state(consent_type, subject):
    base = consent_type.consentdecision_set.filter(
        subject_person=subject, valid_from__lte=timezone.now()
    )
    if base.filter(models.Q(revoked_at__isnull=False) | models.Q(decision="revoked")).exists():
        return "not_allowed"
    decisions = []
    seen = set()
    for item in base.order_by("deciding_person_id", "-decided_at", "-id"):
        if item.deciding_person_id not in seen:
            decisions.append(item)
            seen.add(item.deciding_person_id)
    if not decisions or any(item.decision != "granted" for item in decisions):
        return (
            "not_allowed"
            if len({item.decision for item in decisions}) <= 1
            else "clarification_required"
        )
    return "allowed"
