import hashlib
import json
import logging
import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import transaction
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_POST

from .models import (
    AccountDeletionRequest,
    AuditEvent,
    ClassMembership,
    FamilyAccessCode,
    FamilyChildAccount,
    FamilyRegistrationRequest,
    GuardianChildRelationship,
    Invitation,
    Person,
    PushSubscription,
    RegistrationApplication,
    Role,
    RoleAssignment,
    UserAccount,
    UserNotification,
    normalize_login_email,
)
from .policies import active_class_for_user
from .privacy_services import erase_account_data
from .registration import activate, create_application, sanitized_profile_photo, verify_email

logger = logging.getLogger(__name__)


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
                link = f"{settings.WAGTAILADMIN_BASE_URL.rstrip('/')}/registrieren/email/{token}/"
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


@csrf_protect
@require_http_methods(["GET", "POST"])
def invitation_entry(request):
    if request.method == "POST":
        token = request.POST.get("code", "").strip()
        if _rate_limit(request, "invitation-entry"):
            return render(
                request,
                "core/invitation_entry.html",
                {"error": "Bitte versuche es später erneut."},
                status=429,
            )
        if token and FamilyAccessCode.resolve(token):
            return redirect("family-register", token=token)
        return render(
            request,
            "core/invitation_entry.html",
            {"error": "Der Einladungscode ist ungültig oder abgelaufen."},
            status=400,
        )
    return render(request, "core/invitation_entry.html")


@csrf_protect
@require_http_methods(["GET", "POST"])
def family_register(request, token):
    invitation = FamilyAccessCode.resolve(token)
    if invitation is None:
        return render(request, "core/family_invitation_invalid.html", status=410)
    if request.method == "POST":
        if _rate_limit(request, f"family-register:{invitation.id}", limit=8):
            return render(request, "core/family_invitation_invalid.html", status=429)
        submitted = {
            key: request.POST.get(key, "").strip()
            for key in (
                "first_name",
                "last_name",
                "email",
                "adult_2_first_name",
                "adult_2_last_name",
                "adult_2_email",
                "child_1_first_name",
                "child_1_last_name",
                "child_1_email",
                "child_2_first_name",
                "child_2_last_name",
                "child_2_email",
                "household_label",
            )
        }
        children = []
        for index in (1, 2):
            first = request.POST.get(f"child_{index}_first_name", "").strip()[:100]
            last = request.POST.get(f"child_{index}_last_name", "").strip()[:100]
            email = normalize_login_email(request.POST.get(f"child_{index}_email", ""))
            password = request.POST.get(f"child_{index}_password", "")
            if any((first, last, email, password)) and not all((first, last, email, password)):
                raise_error = (
                    f"Bitte gib für Kind {index} Vorname, Nachname, E-Mail-Adresse "
                    "und ein eigenes Passwort an."
                )
                return render(
                    request,
                    "core/family_register.html",
                    {"invitation": invitation, "error": raise_error, "submitted": submitted},
                    status=400,
                )
            if first and last:
                try:
                    validate_email(email)
                    validate_password(password)
                except ValidationError as exc:
                    return render(
                        request,
                        "core/family_register.html",
                        {
                            "invitation": invitation,
                            "error": f"Kind {index}: {' '.join(exc.messages)}",
                            "submitted": submitted,
                        },
                        status=400,
                    )
                children.append(
                    {
                        "first_name": first,
                        "last_name": last,
                        "email": email,
                        "password": password,
                    }
                )
        adults = []
        second_email = normalize_login_email(request.POST.get("adult_2_email", ""))
        second_first = request.POST.get("adult_2_first_name", "").strip()[:100]
        second_last = request.POST.get("adult_2_last_name", "").strip()[:100]
        if any((second_email, second_first, second_last)) and not all(
            (second_email, second_first, second_last)
        ):
            return render(
                request,
                "core/family_register.html",
                {
                    "invitation": invitation,
                    "error": "Bitte fülle für die zweite erwachsene Person alle drei Felder aus oder lasse sie vollständig leer.",
                    "submitted": submitted,
                },
                status=400,
            )
        if second_email and second_first and second_last:
            adults.append(
                {"email": second_email, "first_name": second_first, "last_name": second_last}
            )
        try:
            if request.POST.get("privacy_ack") != "yes":
                raise ValidationError("Bitte bestätige die Datenschutzinformationen.")
            if not children:
                raise ValidationError("Bitte gib mindestens ein Kind an.")
            first_email = normalize_login_email(request.POST.get("email", ""))
            all_emails = [first_email, second_email] + [child["email"] for child in children]
            all_emails = [email for email in all_emails if email]
            if len(all_emails) != len(set(all_emails)):
                raise ValidationError("Jede Person benötigt eine eigene E-Mail-Adresse.")
            child_emails = [child["email"] for child in children]
            if UserAccount.objects.filter(email__in=child_emails).exists():
                raise ValidationError(
                    "Für mindestens ein Kind besteht bereits ein aktiver Zugang. Bitte verwende dessen vorhandenen Login."
                )
            if RegistrationApplication.objects.filter(email__in=child_emails).exists():
                raise ValidationError(
                    "Für mindestens ein Kind läuft bereits eine Anmeldung. Bitte schließe diese zuerst ab oder lasse sie in der Verwaltung zurücksetzen."
                )
            with transaction.atomic():
                locked = FamilyAccessCode.resolve(token, for_update=True)
                if locked is None:
                    raise ValidationError("Diese Einladung wurde bereits verwendet.")
                item, email_token = create_application(
                    email=request.POST.get("email", ""),
                    first_name=request.POST.get("first_name", ""),
                    last_name=request.POST.get("last_name", ""),
                    password=request.POST.get("password", ""),
                    refresh_unverified=True,
                )
                if not item or not email_token:
                    raise ValidationError(
                        "Für diese E-Mail-Adresse besteht bereits ein bestätigter Antrag oder Zugang. Bitte melde dich damit an oder verwende eine andere persönliche E-Mail-Adresse."
                    )
                family = FamilyRegistrationRequest.objects.create(
                    access_code=locked,
                    household_label=request.POST.get("household_label", "").strip()[:120]
                    or f"Familie {item.last_name}",
                    additional_adults=adults,
                    children=[
                        {"first_name": child["first_name"], "last_name": child["last_name"]}
                        for child in children
                    ],
                )
                for child in children:
                    FamilyChildAccount.objects.create(
                        family_request=family,
                        first_name=child["first_name"],
                        last_name=child["last_name"],
                        email=child["email"],
                        password_hash=make_password(child["password"]),
                    )
                item.school = locked.school_class.school
                item.school_class = locked.school_class
                item.family_request = family
                item.save(update_fields=["school", "school_class", "family_request", "updated_at"])
                locked.submitted_at = timezone.now()
                locked.use_count += 1
                locked.save(update_fields=["submitted_at", "use_count"])
                link = (
                    f"{settings.WAGTAILADMIN_BASE_URL.rstrip('/')}/registrieren/email/{email_token}/"
                )
                send_mail(
                    "E-Mail-Adresse für KlassID bestätigen",
                    f"Öffne diesen einmaligen Link innerhalb von 24 Stunden: {link}",
                    settings.DEFAULT_FROM_EMAIL,
                    [item.email],
                    fail_silently=False,
                )
            return render(request, "core/family_registration_received.html", status=202)
        except ValidationError as exc:
            return render(
                request,
                "core/family_register.html",
                {
                    "invitation": invitation,
                    "error": " ".join(exc.messages),
                    "submitted": submitted,
                },
                status=400,
            )
        except Exception:
            logger.exception("Family registration email could not be sent")
            return render(
                request,
                "core/family_register.html",
                {
                    "invitation": invitation,
                    "error": "Die Bestätigungs-E-Mail konnte gerade nicht versendet werden. Der Einladungscode bleibt gültig; bitte versuche es später erneut.",
                    "submitted": submitted,
                },
                status=503,
            )
    return render(request, "core/family_register.html", {"invitation": invitation})


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
        try:
            person.home_latitude = request.POST.get("home_latitude") or None
            person.home_longitude = request.POST.get("home_longitude") or None
        except (TypeError, ValueError):
            person.home_latitude = person.home_longitude = None
        person.phone = request.POST.get("phone", "").strip()[:50]
        person.chat_display_name = request.POST.get("chat_display_name", "").strip()[:80]
        mode = request.POST.get("contribution_name_mode", "family")
        person.contribution_name_mode = (
            mode if mode in {"family", "child", "personal"} else "family"
        )
        person.email_visibility = (
            "members" if request.POST.get("share_email") == "yes" else "hidden"
        )
        person.phone_visibility = (
            "members" if request.POST.get("share_phone") == "yes" else "hidden"
        )
        photo = request.FILES.get("profile_photo")
        if photo:
            encoded = sanitized_profile_photo(photo)
            person.profile_photo.save(
                f"{secrets.token_urlsafe(18)}.webp", ContentFile(encoded), save=False
            )
        person.full_clean()
        person.save()
        if previous != (person.email_visibility, person.phone_visibility):
            AuditEvent.objects.create(
                actor=request.user,
                action="profile.contact_sharing.changed",
                target_type="person",
                target_id=str(person.pk),
                metadata={
                    "email_shared": person.email_visibility == "members",
                    "phone_shared": person.phone_visibility == "members",
                },
            )
        messages.success(request, "Dein Profil wurde gespeichert.")
        return redirect("personal-profile")
    return render(
        request, "ui/personal_profile.html", {"page_title": "Persönliches Profil", "person": person}
    )


@login_required
@require_http_methods(["GET", "POST"])
def delete_account(request):
    if request.method == "POST":
        password = request.POST.get("password", "")
        confirmation = request.POST.get("confirmation", "").strip().casefold()
        if not request.user.check_password(password) or confirmation != "konto löschen":
            return render(
                request,
                "ui/delete_account.html",
                {
                    "page_title": "Konto und Daten löschen",
                    "error": "Passwort oder Bestätigungstext ist nicht korrekt.",
                },
                status=400,
            )
        deletion, _ = AccountDeletionRequest.objects.get_or_create(
            user=request.user, defaults={"execute_after": timezone.now()}
        )
        erase_account_data(deletion)
        logout(request)
        return render(request, "ui/account_deleted.html", status=200)
    return render(request, "ui/delete_account.html", {"page_title": "Konto und Daten löschen"})


@login_required
def profile_photo(request, person_id):
    from .models import ClassMembership, Person

    school_class = active_class_for_user(request.user)
    person = Person.objects.filter(pk=person_id, profile_photo__gt="").first()
    if (
        not school_class
        or not person
        or not ClassMembership.objects.filter(
            school_class=school_class, person=person, status="active"
        ).exists()
    ):
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
    return render(
        request,
        "ui/notification_list.html",
        {
            "page_title": "Benachrichtigungen",
            "notifications": items,
            "unread_count": items.filter(read_at__isnull=True).count(),
        },
    )


@login_required
@require_POST
def notification_read(request, notification_id):
    school_class = active_class_for_user(request.user)
    with transaction.atomic():
        item = (
            UserNotification.objects.select_for_update()
            .filter(pk=notification_id, user=request.user, school_class=school_class)
            .first()
        )
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
    UserNotification.objects.filter(
        user=request.user, school_class=school_class, read_at__isnull=True
    ).update(read_at=timezone.now())
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
    if invitation.school_class_id:
        person, _ = Person.objects.get_or_create(
            user=user,
            defaults={
                "first_name": invitation.first_name or "Familienmitglied",
                "last_name": invitation.last_name,
            },
        )
        ClassMembership.objects.get_or_create(
            school_class=invitation.school_class,
            person=person,
            defaults={"valid_from": timezone.localdate(), "status": "active"},
        )
        RoleAssignment.objects.get_or_create(
            user=user,
            school=invitation.school_class.school,
            school_class=invitation.school_class,
            role=Role.GUARDIAN,
            defaults={"assigned_by": invitation.invited_by},
        )
        if invitation.household_id:
            invitation.household.members.add(person)
            children = Person.objects.filter(
                households=invitation.household,
                studentprofile__isnull=False,
                classmembership__school_class=invitation.school_class,
            )
            for child in children:
                GuardianChildRelationship.objects.get_or_create(
                    guardian_person=person,
                    student_person=child,
                    defaults={
                        "relationship_type": "guardian",
                        "is_legal_guardian": True,
                        "may_view_student_profile": True,
                        "may_manage_profile": True,
                        "may_manage_general_consents": True,
                        "may_manage_photo_consents": True,
                        "may_manage_biometric_consents": True,
                        "valid_from": timezone.localdate(),
                        "status": "verified",
                        "verified_by": invitation.invited_by,
                        "verified_at": timezone.now(),
                    },
                )
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
    return JsonResponse(
        {"supported": bool(settings.VAPID_PUBLIC_KEY), "public_key": settings.VAPID_PUBLIC_KEY}
    )


@login_required
@require_POST
def push_self_test(request):
    from web_push_kit import DeliveryStatus, NotificationPayload, Subscription

    from klasse5e.webuntis.notifications import configured_sender

    if _rate_limit(request, f"push-self-test:{request.user.pk}", limit=3):
        return JsonResponse({"status": "rate_limited"}, status=429)
    subscription_id = request.POST.get("subscription_id")
    stored = PushSubscription.objects.filter(
        pk=subscription_id, user=request.user, enabled=True
    ).first()
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
    AuditEvent.objects.create(
        actor=request.user,
        action="push.self_test",
        target_type="push_subscription",
        target_id=str(subscription_id),
        metadata={"result": result.status.value, "message_id": message_id},
    )
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
