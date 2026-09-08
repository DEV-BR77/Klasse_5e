from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from .models import AuditEvent, Role, RoleAssignment, UserAccount
from .policies import has_active_membership


def require_role_manager(user):
    if not user.is_authenticated or not user.is_active or user.locked_at:
        raise PermissionDenied
    if not (user.is_superuser or RoleAssignment.objects.filter(
        user=user, active=True, role__in=[Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN],
        school__isnull=True, school_class__isnull=True,
    ).exists()):
        raise PermissionDenied


@transaction.atomic
def set_user_role(actor, user, role, *, school_class=None, active=True):
    # Serialize role administration, including simultaneous administrator revocations.
    list(UserAccount.objects.select_for_update().order_by("pk").values_list("pk", flat=True))
    require_role_manager(actor)
    if role not in {Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN, Role.PARENT_REPRESENTATIVE}:
        raise ValidationError("Diese Rolle kann hier nicht vergeben werden.")
    if role in {Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN}:
        if school_class is not None:
            raise ValidationError("Portal-Administratoren gelten portalweit.")
        if actor.pk == user.pk and not active:
            raise ValidationError("Die eigene Portal-Adminrolle kann hier nicht entzogen werden.")
    elif school_class is None or (active and not has_active_membership(user, school_class)):
        raise ValidationError("Elternvertretungen benötigen einen aktiven Zugang zur gewählten Klasse.")
    if active and (not user.is_active or user.locked_at):
        raise ValidationError("Das Konto ist nicht aktiv.")
    assignments = RoleAssignment.objects.filter(user=user, role=role, school_class=school_class, school=None)
    assignment = assignments.first()
    if assignment is None:
        if not active:
            return
        assignment = RoleAssignment.objects.create(
            user=user, role=role, school_class=school_class, assigned_by=actor,
        )
    else:
        assignments.update(active=active, assigned_by=actor)
    AuditEvent.objects.create(
        actor=actor, action="role.granted" if active else "role.revoked",
        target_type="user", target_id=str(user.pk),
        metadata={"role": role, "school_class_id": school_class.pk if school_class else None},
    )


def parent_representatives(school_class):
    users = UserAccount.objects.filter(
        roleassignment__role=Role.PARENT_REPRESENTATIVE,
        roleassignment__school_class=school_class, roleassignment__active=True,
        is_active=True, locked_at__isnull=True,
    ).distinct()
    return [user for user in users if has_active_membership(user, school_class)]
