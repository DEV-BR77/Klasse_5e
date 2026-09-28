"""One catalogue for personal theme selection, preview and persistence."""

from django.db.models import Q

from .models import PortalTheme, Role, StudentProfile


def can_manage_themes(user):
    return user.is_superuser or user.roleassignment_set.filter(
        active=True, role__in=[Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN]
    ).exists()


def available_themes(user, *, include_drafts=False):
    themes = PortalTheme.objects.all()
    if can_manage_themes(user):
        return themes if include_drafts else themes.filter(is_active=True)
    audience = (
        PortalTheme.Audience.CHILDREN
        if StudentProfile.objects.filter(person__user=user).exists()
        else PortalTheme.Audience.ADULTS
    )
    return themes.filter(is_active=True).filter(
        Q(audience=PortalTheme.Audience.ALL) | Q(audience=audience)
    )
