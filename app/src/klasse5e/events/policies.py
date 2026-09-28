from klasse5e.core.models import Role
from klasse5e.core.module_permissions import may_manage_module
from klasse5e.core.policies import has_active_membership


def may_create_event(user, school_class):
    return all(may_manage_module(
        user, "events", action, school_class, owner_id=user.pk,
        legacy_roles={Role.DEPUTY_ADMIN, Role.SCHOOL_ADMIN, Role.CLASS_ADMIN},
    ) for action in ("create", "publish"))


def may_manage_event(user, event):
    owner = event.organizers.filter(pk=user.pk).exists()
    return (owner and has_active_membership(user, event.school_class)) or may_manage_module(
        user, "events", "edit", event.school_class,
        owner_id=user.pk if owner else None,
    )
