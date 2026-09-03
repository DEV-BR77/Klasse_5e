from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404

from .models import AuditEvent, PortalModule, PortalModuleOverride, Role, UserNotification
from .policies import active_class_for_user

MODULE_PATHS = {
    "/documents/": "pdf_forms",
    "/mehr/dokumente/": "pdf_forms",
    "/mehr/fotos/": "gallery",
    "/galleries/": "gallery",
    "/photos/": "gallery",
    "/biometrics/": "photo_memory",
    "/chat/": "chat",
    "/webuntis/": "webuntis_timetable",
    "/mehr/webuntis/": "webuntis_timetable",
    "/itslearning/": "itslearning",
    "/contacts/": "contacts",
    "/calendar/": "calendar",
    "/kalender/": "calendar",
    "/schedule/": "calendar",
    "/mehr/veranstaltungen/": "events",
    "/events/": "events",
    "/items/": "events",
    "/reservations/": "events",
    "/mehr/mobilitaet/": "mobility",
    "/mobility/": "mobility",
    "/push/": "push",
}


def module_enabled(key, school_class=None):
    module = PortalModule.objects.filter(key=key).first()
    if module is None:
        return False
    if school_class:
        override = PortalModuleOverride.objects.filter(
            module=module, school_class=school_class
        ).first()
        if override:
            return override.enabled
        override = PortalModuleOverride.objects.filter(
            module=module, school=school_class.school
        ).first()
        if override:
            return override.enabled
    override = PortalModuleOverride.objects.filter(
        module=module, school__isnull=True, school_class__isnull=True
    ).first()
    return override.enabled if override else module.default_enabled


def module_context(request):
    if not request.user.is_authenticated:
        return {"enabled_modules": {}, "personal_display_name": "", "current_theme": None}
    school_class = active_class_for_user(request.user) if request.user.is_authenticated else None
    keys = PortalModule.objects.values_list("key", flat=True)
    unread_count = 0
    if school_class:
        unread_count = UserNotification.objects.filter(
            user=request.user, school_class=school_class, read_at__isnull=True
        ).count()
    return {
        "enabled_modules": {key: module_enabled(key, school_class) for key in keys},
        "personal_display_name": (
            request.user.person.first_name
            if request.user.is_authenticated and hasattr(request.user, "person")
            else ""
        ),
        "notification_unread_count": unread_count,
        "current_theme": request.user.selected_theme if request.user.selected_theme_id and request.user.selected_theme.is_active else None,
        "can_manage_portal": request.user.is_superuser
        or request.user.roleassignment_set.filter(
            active=True,
            role__in=[Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN, Role.SCHOOL_ADMIN, Role.CLASS_ADMIN],
        ).exists(),
    }


@transaction.atomic
def set_module_override(*, key, enabled, actor, school=None, school_class=None, reason=""):
    module = PortalModule.objects.select_for_update().get(key=key)
    if enabled:
        for dependency in module.dependencies:
            target_class = school_class
            if not module_enabled(dependency, target_class):
                raise ValidationError(f"Abhängiges Modul ist deaktiviert: {dependency}")
    item, _ = PortalModuleOverride.objects.update_or_create(
        module=module,
        school=school,
        school_class=school_class,
        defaults={"enabled": enabled, "updated_by": actor, "reason": reason[:300]},
    )
    AuditEvent.objects.create(
        actor=actor,
        action="module.override.changed",
        target_type="portal_module",
        target_id=key,
        metadata={
            "enabled": enabled,
            "school_id": school.pk if school else None,
            "class_id": school_class.pk if school_class else None,
        },
    )
    return item


class ModuleGateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for prefix, key in MODULE_PATHS.items():
            if request.path.startswith(prefix):
                school_class = active_class_for_user(request.user) if request.user.is_authenticated else None
                if not module_enabled(key, school_class):
                    raise Http404
                break
        return self.get_response(request)
