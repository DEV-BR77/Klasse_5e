from allauth.account.adapter import DefaultAccountAdapter
from allauth.mfa.adapter import DefaultMFAAdapter
from django.conf import settings

from .models import normalize_login_email


class ClosedAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False

    def clean_email(self, email):
        return normalize_login_email(super().clean_email(email))


class KlassIDMFAAdapter(DefaultMFAAdapter):
    """Keep configured authenticators while allowing a narrow test bypass."""

    def is_mfa_enabled(self, user, types=None):
        is_top_level_admin = (
            user.is_authenticated
            and user.roleassignment_set.filter(
                active=True, role__in=["primary_admin", "deputy_admin"]
            ).exists()
        )
        if (
            settings.TEMPORARY_ADMIN_MFA_BYPASS
            and user.is_authenticated
            and (user.is_staff or user.is_superuser or is_top_level_admin)
        ):
            return False
        return super().is_mfa_enabled(user, types=types)
