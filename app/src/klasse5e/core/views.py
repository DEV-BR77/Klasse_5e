import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.contrib.sessions.models import Session
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_POST

from .models import AuditEvent, Invitation, PushSubscription


def health(request):
    return JsonResponse({"status": "ok"})


@login_required
def dashboard(request):
    return render(request, "core/dashboard.html")


@csrf_protect
@require_http_methods(["GET", "POST"])
def accept_invitation(request, token):
    if request.method == "GET":
        return render(request, "core/accept_invitation.html")
    password = request.POST.get("password", "")
    try:
        validate_password(password)
    except Exception:
        return HttpResponse("Passwort erfüllt die Anforderungen nicht", status=400)
    invitation = Invitation.consume(token)
    if invitation is None:
        return HttpResponse("Einladung ungültig oder abgelaufen", status=410)
    User = get_user_model()
    user = User.objects.filter(email__iexact=invitation.email).first()
    if user and user.is_active:
        return HttpResponse("Konto existiert bereits", status=409)
    if user is None:
        user = User.objects.create_user(email=invitation.email, password=password, is_active=True)
    else:
        user.set_password(password)
        user.is_active = True
    user.email_verified_at = invitation.used_at
    user.save()
    AuditEvent.objects.create(
        actor=user, action="invitation.accepted", target_type="user", target_id=str(user.pk)
    )
    return redirect("account_login")


@login_required
@require_POST
def revoke_all_sessions(request):
    for session in Session.objects.filter(
        expire_date__gte=__import__("django.utils.timezone").utils.timezone.now()
    ):
        data = session.get_decoded()
        if str(data.get("_auth_user_id")) == str(request.user.pk):
            session.delete()
    AuditEvent.objects.create(
        actor=request.user,
        action="sessions.revoked_all",
        target_type="user",
        target_id=str(request.user.pk),
    )
    return JsonResponse({"revoked": True})


@login_required
@require_http_methods(["POST", "DELETE"])
def push_subscriptions(request):
    payload = json.loads(request.body or b"{}")
    endpoint = payload.get("endpoint", "")
    if request.method == "DELETE":
        import hashlib

        PushSubscription.objects.filter(
            user=request.user, endpoint_hash=hashlib.sha256(endpoint.encode()).hexdigest()
        ).delete()
        return JsonResponse({"removed": True})
    keys = payload.get("keys", {})
    PushSubscription.from_values(
        request.user, endpoint, keys.get("p256dh", ""), keys.get("auth", "")
    )
    return JsonResponse({"subscribed": True}, status=201)


def manifest(request):
    return JsonResponse(
        {
            "name": "Klasse 5e",
            "short_name": "Klasse 5e",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#174b7a",
            "icons": [
                {
                    "src": "/static/icons/icon.svg",
                    "sizes": "any",
                    "type": "image/svg+xml",
                    "purpose": "any maskable",
                }
            ],
        }
    )


def service_worker(request):
    script = """const CACHE='klasse5e-shell-v1';self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(['/offline/','/static/app.css']))));self.addEventListener('fetch',e=>{if(e.request.mode==='navigate')e.respondWith(fetch(e.request).catch(()=>caches.match('/offline/')))});"""
    return HttpResponse(script, content_type="application/javascript")


def offline(request):
    return render(request, "core/offline.html")
