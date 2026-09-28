"""Effective managed-role permissions; never a replacement for object policies."""

from django.db.models import Q

from .models import Role, RoleAssignment, RoleModulePermission
from .policies import active_roles, has_active_membership


MANAGED_ROLES = {Role.PRIMARY_ADMIN, Role.CONTENT_MANAGER, Role.EDITOR, Role.MODERATOR}

# Only expose controls that have a corresponding domain operation. Personal
# school connections, contacts and push subscriptions are governed by their
# own relationship/consent/ownership policies, not by an administrative grant.
MODULE_ACTIONS = {
    "pdf_forms": {"view", "read"},
    "gallery": {"view", "read", "create", "moderate", "publish"},
    "photo_memory": {"view", "read", "moderate"},
    "chat": {"view", "read", "create", "edit", "moderate", "publish"},
    "calendar": {"view", "read", "edit"},
    "events": {"view", "read", "create", "edit", "publish"},
    "mobility": {"view", "read", "moderate"},
}

MODULE_DESCRIPTIONS = {
    "chat": "Erstellen legt Räume an. Bearbeiten ändert Räume. Moderieren verwaltet Mitglieder, archiviert/löscht Räume und blendet Nachrichten aus. Veröffentlichen erlaubt Rolleninhabern ohne eigene Klassenmitgliedschaft das Schreiben.",
    "events": "Erstellen und Veröffentlichen werden gemeinsam für neue Veranstaltungen und Terminumfragen benötigt. Bearbeiten verwaltet bestehende Veranstaltungen einschließlich Mitbringlisten und Löschen.",
    "gallery": "Erstellen und Veröffentlichen erlauben neue Galerien. Moderieren prüft Bilder; für deren Freigabe ist zusätzlich Veröffentlichen erforderlich. Eigene Daten bezieht sich auf selbst angelegte Galerien.",
    "calendar": "Bearbeiten ändert manuelle Kalendereinträge. Persönliche Schulimporte bleiben an ihre Zugangsfreigaben gebunden.",
    "photo_memory": "Lesen erlaubt die rollenbezogene Suche, Moderieren die Verwaltung. Aktivierung, Klassenzugehörigkeit und biometrische Einwilligungen sind weiterhin erforderlich.",
    "pdf_forms": "Lesen erlaubt den rollenbezogenen Abruf veröffentlichter Dokumente innerhalb der zugewiesenen Schule oder Klasse.",
    "mobility": "Moderieren erlaubt die Moderation von Angeboten im berechtigten Klassenbereich. Private Abholfreigaben werden dadurch nicht erweitert.",
}


def _role_grants(user, module_key, action, school_class, owner_id):
    if not getattr(user, "is_authenticated", False) or not user.is_active or user.locked_at:
        return set()
    if school_class is None or action not in MODULE_ACTIONS.get(module_key, set()):
        return set()
    from .module_flags import module_enabled

    if not module_enabled(module_key, school_class):
        return set()
    required = {"view", action}
    if action != "view":
        required.add("read")
    assignments = RoleAssignment.objects.filter(
        user=user, active=True, role__in=MANAGED_ROLES,
    ).filter(
        Q(school_class=school_class)
        | Q(school=school_class.school, school_class__isnull=True)
        | Q(school__isnull=True, school_class__isnull=True)
    )
    roles = set(assignments.values_list("role", flat=True))
    permissions = RoleModulePermission.objects.filter(
        role__in=roles, module__key=module_key, action__in=required, active=True,
    ).values_list("role", "action", "scope")
    member = has_active_membership(user, school_class)
    grants = {}
    for role, granted_action, scope in permissions:
        if scope not in RoleModulePermission.Scope.values:
            continue
        if scope == RoleModulePermission.Scope.OWN and owner_id != user.pk:
            continue
        # Assignments are already intersected with the target class. Platform
        # never widens a school/class assignment. Non-admin roles additionally
        # require a current membership (including a verified child's class).
        if not member and not (
            role == Role.PRIMARY_ADMIN and scope == RoleModulePermission.Scope.PLATFORM
        ):
            continue
        grants.setdefault(role, set()).add(granted_action)
    return {role for role, actions in grants.items() if required <= actions}


def role_allows_module_action(user, module_key, action, school_class, *, owner_id=None):
    """Check a managed role's grant within its assignment and class boundary.

    A grant does not expose an object: callers must still apply their room,
    event, gallery, consent and publication policies. Unmanaged roles retain
    their existing feature-specific authorization paths.
    """
    return bool(_role_grants(user, module_key, action, school_class, owner_id))


def effective_module_roles(user, module_key, action, school_class, *, owner_id=None):
    """Apply the matrix to managed roles and preserve other domain roles."""
    roles = active_roles(user, school_class)
    return (roles - MANAGED_ROLES) | _role_grants(
        user, module_key, action, school_class, owner_id,
    )


def may_manage_module(user, module_key, action, school_class, *, legacy_roles=(), owner_id=None):
    if not getattr(user, "is_authenticated", False) or not user.is_active or user.locked_at:
        return False
    from .module_flags import module_enabled

    if not module_enabled(module_key, school_class):
        return False
    return bool(
        user.is_superuser
        or (active_roles(user, school_class) - MANAGED_ROLES) & set(legacy_roles)
        or role_allows_module_action(user, module_key, action, school_class, owner_id=owner_id)
    )


def may_access_module(user, module_key, school_class, *, owner_id=None):
    from .module_flags import module_enabled

    if school_class is None or not module_enabled(module_key, school_class):
        return False
    return has_active_membership(user, school_class) or may_manage_module(
        user, module_key, "read", school_class,
        legacy_roles={Role.DEPUTY_ADMIN, Role.SCHOOL_ADMIN, Role.CLASS_ADMIN},
        owner_id=owner_id,
    )
