from allauth.account.adapter import DefaultAccountAdapter
from allauth.mfa.adapter import DefaultMFAAdapter
from django.conf import settings
from django.contrib import messages

from .models import normalize_login_email


class ClosedAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False

    def clean_email(self, email):
        return normalize_login_email(super().clean_email(email))

    def login(self, request, user):
        super().login(request, user)
        from .leak_checks import inspect_successful_login

        email_found, password_found = inspect_successful_login(user, request.POST.get("password", ""))
        if password_found:
            messages.error(request, "Dein Passwort wurde in bekannten Datenlecks gefunden. Bitte ändere es sofort.")
        elif email_found:
            messages.warning(request, "Deine E-Mail-Adresse wurde in bekannten Datenlecks gefunden. Bitte prüfe und ändere dein Passwort.")

    def get_login_stages(self):
        stages = super().get_login_stages()
        if settings.MFA_LOGIN_DISABLED:
            return [stage for stage in stages if not stage.startswith("allauth.mfa.")]
        return stages


class KlassIDMFAAdapter(DefaultMFAAdapter):
    """Keep configured authenticators while allowing a narrow test bypass."""

    def is_mfa_enabled(self, user, types=None):
        if settings.MFA_LOGIN_DISABLED:
            return False
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
