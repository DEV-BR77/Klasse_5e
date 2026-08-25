import hashlib

from allauth.mfa.models import Authenticator
from django.contrib.auth import logout
from django.core.cache import cache
from django.http import HttpResponse

from .policies import PRIVILEGED_ROLES, active_roles


class ActiveAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
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
    SAFE_PREFIXES = ("/accounts/2fa/", "/accounts/logout/", "/health/", "/static/")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.path.startswith(self.SAFE_PREFIXES):
            if active_roles(request.user) & PRIVILEGED_ROLES:
                has_mfa = Authenticator.objects.filter(
                    user=request.user,
                    type__in=[Authenticator.Type.TOTP, Authenticator.Type.WEBAUTHN],
                ).exists()
                if not has_mfa:
                    return HttpResponse("Zwei-Faktor-Anmeldung erforderlich", status=403)
        return self.get_response(request)
