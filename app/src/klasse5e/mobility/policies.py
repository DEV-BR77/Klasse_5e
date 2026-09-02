from django.db import models
from django.utils import timezone

from klasse5e.core.models import GuardianChildRelationship
from klasse5e.core.policies import has_active_membership


def is_verified_guardian(user, school_class):
    if not has_active_membership(user, school_class) or not hasattr(user, "person"):
        return False
    today = timezone.localdate()
    return (
        GuardianChildRelationship.objects.filter(
            guardian_person=user.person,
            status="verified",
            verified_at__isnull=False,
            is_legal_guardian=True,
            valid_from__lte=today,
            student_person__classmembership__school_class=school_class,
            student_person__classmembership__status="active",
            student_person__classmembership__valid_from__lte=today,
        )
        .filter(models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=today))
        .filter(
            models.Q(student_person__classmembership__valid_until__isnull=True)
            | models.Q(student_person__classmembership__valid_until__gte=today)
        )
        .exists()
    )
