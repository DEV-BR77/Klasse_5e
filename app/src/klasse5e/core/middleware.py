import hashlib

from allauth.mfa.models import Authenticator
from django.conf import settings
from django.contrib.auth import logout
from django.core.cache import cache
from django.core.management import call_command
from django.db.utils import OperationalError, ProgrammingError
from django.http import HttpResponse
from django.shortcuts import redirect

from .onboarding import onboarding_complete
from .policies import PRIVILEGED_ROLES, active_roles


class ActiveAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if cache.add("privacy-retention-reconcile", True, 3600):
            try:
                call_command("process_privacy_retention", verbosity=0)
            except (OperationalError, ProgrammingError):
                cache.delete("privacy-retention-reconcile")
        if request.user.is_authenticated and (not request.user.is_active or request.user.locked_at):
            logout(request)
        return self.get_response(request)


class LoginRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/accounts/login/" and request.method == "POST":
            raw = (
                f"{request.META.get('REMOTE_ADDR', '')}|{request.POST.get('login', '').casefold()}"
            )
            key = "login-rate:" + hashlib.sha256(raw.encode()).hexdigest()
            attempts = cache.get(key, 0) + 1
            cache.set(key, attempts, 300)
            if attempts > 5:
                return HttpResponse("Zu viele Anmeldeversuche", status=429)
        return self.get_response(request)


class PrivilegedMfaMiddleware:
    SAFE_PREFIXES = (
        "/accounts/2fa/",
        "/accounts/logout/",
        "/accounts/reauthenticate/",
        "/health/",
        "/static/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.path.startswith(self.SAFE_PREFIXES):
            roles = active_roles(request.user)
            if roles & PRIVILEGED_ROLES:
                if settings.TEMPORARY_ADMIN_MFA_BYPASS and (
                    request.user.is_staff
                    or request.user.is_superuser
                    or roles & {"primary_admin", "deputy_admin"}
                ):
                    return self.get_response(request)
                has_mfa = Authenticator.objects.filter(
                    user=request.user,
                    type__in=[Authenticator.Type.TOTP, Authenticator.Type.WEBAUTHN],
                ).exists()
                if not has_mfa:
                    return redirect("mfa_activate_totp")
        return self.get_response(request)


class OnboardingRequiredMiddleware:
    EXEMPT_PREFIXES = (
        "/accounts/",
        "/admin/",
        "/cms/",
        "/datenschutz/",
        "/impressum/",
        "/nutzung/",
        "/health/",
        "/invitation/",
        "/einladung/",
        "/projekt/",
        "/demo/",
        "/registrieren/",
        "/aktivieren/",
        "/onboarding/",
        "/static/",
        "/service-worker.js",
        "/manifest.webmanifest",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and request.user.email_verified_at
            and not request.path.startswith(self.EXEMPT_PREFIXES)
        ):
            try:
                if not onboarding_complete(request.user):
                    return redirect("onboarding-resume")
            except (OperationalError, ProgrammingError):
                # Health and deployment stay available while migrations run.
                pass
        return self.get_response(request)
