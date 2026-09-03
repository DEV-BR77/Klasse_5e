import hashlib
import json
import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.db import transaction
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_POST

from .models import AuditEvent, Invitation, PushSubscription, UserNotification
from .policies import active_class_for_user
from .registration import activate, create_application, sanitized_profile_photo, verify_email


def health(request):
    return JsonResponse({"status": "ok"})


def _rate_limit(request, purpose, limit=5):
    material = f"{purpose}|{request.META.get('REMOTE_ADDR', '')}"
    key = "public-rate:" + hashlib.sha256(material.encode()).hexdigest()
    count = cache.get(key, 0) + 1
    cache.set(key, count, 3600)
    return count > limit


@csrf_protect
@require_http_methods(["GET", "POST"])
def register(request):
    if request.method == "POST" and not _rate_limit(request, "register"):
        try:
            item, token = create_application(
                email=request.POST.get("email", ""),
                first_name=request.POST.get("first_name", ""),
                last_name=request.POST.get("last_name", ""),
                password=request.POST.get("password", ""),
            )
            if item and token:
                link = (
                    f"{settings.WAGTAILADMIN_BASE_URL.rstrip('/')}/registrieren/email/{token}/"
                )
                send_mail(
                    "E-Mail-Adresse für KlassID bestätigen",
                    f"Öffne diesen einmaligen Link innerhalb von 24 Stunden: {link}",
                    settings.DEFAULT_FROM_EMAIL,
                    [item.email],
                    fail_silently=False,
                )
        except Exception:
            # The public response deliberately does not reveal accounts or mail state.
            pass
        return render(request, "core/registration_received.html", status=202)
    if request.method == "POST":
        return render(request, "core/registration_received.html", status=202)
    return render(request, "core/register.html")


def verify_registration_email(request, token):
    item = verify_email(token)
    return render(request, "core/registration_verified.html", {"valid": bool(item)})


def activate_registration(request, token):
    user = activate(token)
    return render(request, "core/registration_activated.html", {"valid": bool(user)})


@login_required
@require_http_methods(["GET", "POST"])
def personal_profile(request):
    if not hasattr(request.user, "person"):
        raise Http404
    person = request.user.person
    if request.method == "POST":
        previous = (person.email_visibility, person.phone_visibility)
        person.first_name = request.POST.get("first_name", "").strip()[:100]
        person.last_name = request.POST.get("last_name", "").strip()[:100]
        person.street = request.POST.get("street", "").strip()[:180]
        person.postal_code = request.POST.get("postal_code", "").strip()[:10]
        person.city = request.POST.get("city", "").strip()[:120]
        person.phone = request.POST.get("phone", "").strip()[:50]
        person.email_visibility = "members" if request.POST.get("share_email") == "yes" else "hidden"
        person.phone_visibility = "members" if request.POST.get("share_phone") == "yes" else "hidden"
        photo = request.FILES.get("profile_photo")
        if photo:
            encoded = sanitized_profile_photo(photo)
            person.profile_photo.save(f"{secrets.token_urlsafe(18)}.webp", ContentFile(encoded), save=False)
        person.full_clean()
        person.save()
        if previous != (person.email_visibility, person.phone_visibility):
            AuditEvent.objects.create(
                actor=request.user,
                action="profile.contact_sharing.changed",
                target_type="person",
                target_id=str(person.pk),
                metadata={"email_shared": person.email_visibility == "members", "phone_shared": person.phone_visibility == "members"},
            )
        messages.success(request, "Dein Profil wurde gespeichert.")
        return redirect("personal-profile")
    return render(request, "ui/personal_profile.html", {"page_title": "Persönliches Profil", "person": person})


@login_required
def profile_photo(request, person_id):
    from .models import ClassMembership, Person

    school_class = active_class_for_user(request.user)
    person = Person.objects.filter(pk=person_id, profile_photo__gt="").first()
    if not school_class or not person or not ClassMembership.objects.filter(
        school_class=school_class, person=person, status="active"
    ).exists():
        raise Http404
    response = FileResponse(person.profile_photo.open("rb"), content_type="image/webp")
    response["Cache-Control"] = "private, max-age=300"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@login_required
def notification_list(request):
    school_class = active_class_for_user(request.user)
    if not school_class:
        raise Http404
    items = UserNotification.objects.filter(user=request.user, school_class=school_class)
    return render(request, "ui/notification_list.html", {"page_title": "Benachrichtigungen", "notifications": items, "unread_count": items.filter(read_at__isnull=True).count()})


@login_required
@require_POST
def notification_read(request, notification_id):
    school_class = active_class_for_user(request.user)
    with transaction.atomic():
        item = UserNotification.objects.select_for_update().filter(pk=notification_id, user=request.user, school_class=school_class).first()
        if not item:
            raise Http404
        if item.read_at is None:
            item.read_at = timezone.now()
            item.save(update_fields=["read_at"])
    return redirect(item.target_url)


@login_required
@require_POST
def notifications_read_all(request):
    school_class = active_class_for_user(request.user)
    if not school_class:
        raise Http404
    UserNotification.objects.filter(user=request.user, school_class=school_class, read_at__isnull=True).update(read_at=timezone.now())
    return redirect("notification-list")


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
    try:
        payload = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid_payload"}, status=400)
    endpoint = str(payload.get("endpoint", "")).strip()
    if not endpoint:
        return JsonResponse({"error": "endpoint_required"}, status=400)
    if request.method == "DELETE":
        import hashlib

        removed = PushSubscription.objects.filter(
            user=request.user, endpoint_hash=hashlib.sha256(endpoint.encode()).hexdigest()
        ).update(enabled=False)
        return JsonResponse({"removed": bool(removed)})
    keys = payload.get("keys", {})
    p256dh, auth = str(keys.get("p256dh", "")).strip(), str(keys.get("auth", "")).strip()
    if not p256dh or not auth:
        return JsonResponse({"error": "keys_required"}, status=400)
    try:
        stored, _ = PushSubscription.from_values(
            request.user,
            endpoint,
            p256dh,
            auth,
            str(payload.get("device_label", "")).strip(),
        )
    except ValidationError:
        return JsonResponse({"error": "subscription_not_owned"}, status=409)
    return JsonResponse({"subscribed": True, "subscription_id": stored.pk}, status=201)


@login_required
def push_configuration(request):
    return JsonResponse({"supported": bool(settings.VAPID_PUBLIC_KEY), "public_key": settings.VAPID_PUBLIC_KEY})


@login_required
@require_POST
def push_self_test(request):
    from web_push_kit import DeliveryStatus, NotificationPayload, Subscription

    from klasse5e.webuntis.notifications import configured_sender

    if _rate_limit(request, f"push-self-test:{request.user.pk}", limit=3):
        return JsonResponse({"status": "rate_limited"}, status=429)
    subscription_id = request.POST.get("subscription_id")
    stored = PushSubscription.objects.filter(pk=subscription_id, user=request.user, enabled=True).first()
    sender = configured_sender()
    if not stored or sender is None:
        return JsonResponse({"status": "not_configured"}, status=409)
    message_id = f"selftest-{request.user.pk}-{secrets.token_hex(8)}"
    result = sender.send(
        Subscription(endpoint=stored.endpoint, p256dh=stored.p256dh, auth=stored.auth),
        NotificationPayload(
            title="KlassID-Test",
            body="Push-Benachrichtigungen funktionieren auf diesem Gerät.",
            url="/mehr/benachrichtigungen/",
            category="self_test",
            message_id=message_id,
        ),
    )
    if result.status == DeliveryStatus.STALE:
        stored.delete()
    AuditEvent.objects.create(actor=request.user, action="push.self_test", target_type="push_subscription", target_id=str(subscription_id), metadata={"result": result.status.value, "message_id": message_id})
    return JsonResponse({"status": result.status.value, "message_id": message_id})


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
                    "src": "/static/icons/klassid.svg",
                    "sizes": "any",
                    "type": "image/svg+xml",
                    "purpose": "any maskable",
                }
            ],
        }
    )


def service_worker(request):
    script = """const CACHE='klassid-shell-v3';self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(['/offline/','/static/app.css?v=3']))));self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))));self.addEventListener('fetch',e=>{if(e.request.mode==='navigate')e.respondWith(fetch(e.request).catch(()=>caches.match('/offline/')))});self.addEventListener('push',e=>{let d={title:'KlassID',body:'Neue geschützte Information',url:'/'};try{d={...d,...e.data.json()}}catch(_){}e.waitUntil(self.registration.showNotification(d.title,{body:d.body,tag:d.tag||d.message_id,data:{url:d.url},icon:d.icon||'/static/icons/klassid.svg'}))});self.addEventListener('notificationclick',e=>{e.notification.close();e.waitUntil(clients.openWindow(e.notification.data?.url||'/'))});"""
    return HttpResponse(script, content_type="application/javascript")


def offline(request):
    return render(request, "core/offline.html")
