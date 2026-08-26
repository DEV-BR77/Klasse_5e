from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from klasse5e.core.models import (
    ConsentDecision,
    ConsentType,
    GuardianChildRelationship,
    Role,
)
from klasse5e.core.policies import active_roles, has_active_membership


def feature_enabled():
    return bool(settings.BIOMETRIC_SEARCH_ENABLED)


def _current_guardians(student_person):
    today = timezone.localdate()
    return list(
        GuardianChildRelationship.objects.filter(
            student_person=student_person,
            status="verified",
            verified_at__isnull=False,
            may_manage_biometric_consents=True,
            valid_from__lte=today,
        ).filter(Q(valid_until__isnull=True) | Q(valid_until__gte=today))
    )


def biometric_consent(student_person, key="biometric-search"):
    consent_type = ConsentType.objects.filter(key=key, category="biometric").first()
    guardians = _current_guardians(student_person)
    if not consent_type or not guardians:
        return False, "missing_consent"
    now = timezone.now()
    for relation in guardians:
        decision = (
            ConsentDecision.objects.filter(
                consent_type=consent_type,
                subject_person=student_person,
                deciding_person=relation.guardian_person,
                valid_from__lte=now,
            )
            .filter(Q(valid_until__isnull=True) | Q(valid_until__gt=now))
            .order_by("-decided_at", "-id")
            .first()
        )
        if not decision or decision.decision != "granted" or decision.revoked_at:
            return False, "missing_or_conflicting_guardian_consent"
    return True, "allowed"


def biometric_consent_version(student_person, key="biometric-search"):
    consent_type = ConsentType.objects.filter(key=key, category="biometric").first()
    if not consent_type:
        return ""
    versions = []
    for relation in _current_guardians(student_person):
        decision = (
            ConsentDecision.objects.filter(
                consent_type=consent_type,
                subject_person=student_person,
                deciding_person=relation.guardian_person,
                valid_from__lte=timezone.now(),
            )
            .filter(Q(valid_until__isnull=True) | Q(valid_until__gt=timezone.now()))
            .select_related("text_version")
            .order_by("-decided_at", "-id")
            .first()
        )
        if decision:
            versions.append(decision.text_version.version)
    return ",".join(sorted(set(versions)))[:32]


def may_manage_biometrics(user, school_class):
    return bool(
        feature_enabled()
        and has_active_membership(user, school_class)
        and active_roles(user, school_class)
        & {Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN, Role.MODERATOR}
    )


def may_search_profile(user, profile):
    if not feature_enabled() or profile.status != "active" or profile.collection.status != "active":
        return False
    school_class = profile.collection.school_class
    if not has_active_membership(user, school_class):
        return False
    consent, _ = biometric_consent(profile.student.person)
    if not consent:
        return False
    roles = active_roles(user, school_class)
    if roles & {Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN, Role.TEACHER, Role.MODERATOR}:
        return True
    if not hasattr(user, "person"):
        return False
    today = timezone.localdate()
    return (
        GuardianChildRelationship.objects.filter(
            guardian_person=user.person,
            student_person=profile.student.person,
            status="verified",
            may_view_student_profile=True,
            valid_from__lte=today,
        )
        .filter(Q(valid_until__isnull=True) | Q(valid_until__gte=today))
        .exists()
    )
