import json
import re
from datetime import date, timedelta
from unittest.mock import Mock, patch

import pytest
from django.core import mail
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.test import override_settings
from django.utils import timezone
from web_push_kit import DeliveryResult, DeliveryStatus

from klasse5e.core.models import (
    ActivationGrant,
    ClassMembership,
    Person,
    PortalModule,
    PortalModuleOverride,
    PushSubscription,
    RegistrationApplication,
    School,
    SchoolClass,
    SchoolYear,
    UserNotification,
)
from klasse5e.core.registration import activate, create_application, verify_email


@pytest.mark.django_db
def test_registration_email_approval_and_activation_are_one_time(school, school_class, admin_user):
    application, email_token = create_application(
        email="pilot@example.test",
        first_name="Müller",
        last_name="Groß-Gerau",
        password="Safe-Test-Password-123!",
    )
    assert application.status == RegistrationApplication.Status.EMAIL_PENDING
    assert verify_email(email_token).status == RegistrationApplication.Status.REVIEW_PENDING
    application.refresh_from_db()
    application.school = school
    application.school_class = school_class
    application.reviewed_by = admin_user
    application.reviewed_at = timezone.now()
    application.status = RegistrationApplication.Status.APPROVED
    application.save()
    _, activation_token = ActivationGrant.issue(application)

    user = activate(activation_token)
    assert user and user.person.first_name == "Müller"
    assert ClassMembership.objects.filter(person=user.person, school_class=school_class).exists()
    assert activate(activation_token) is None


@pytest.mark.django_db
def test_expired_or_revoked_activation_never_creates_access(school, school_class, admin_user):
    application, _ = RegistrationApplication.issue(
        email="expired@example.test",
        first_name="Erika",
        last_name="Beispiel",
        password_hash="not-used",
    )
    application.status = RegistrationApplication.Status.APPROVED
    application.school = school
    application.school_class = school_class
    application.reviewed_by = admin_user
    application.save()
    grant, token = ActivationGrant.issue(application)
    grant.expires_at = timezone.now() - timedelta(seconds=1)
    grant.save()
    assert activate(token) is None


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_public_registration_is_neutral_and_sends_verification(client):
    response = client.post(
        "/registrieren/",
        {"first_name": "Erika", "last_name": "Muster", "email": "new@example.test", "password": "Safe-Test-Password-123!"},
    )
    assert response.status_code == 202
    assert len(mail.outbox) == 1
    assert re.search(r"/registrieren/email/[A-Za-z0-9_-]+/", mail.outbox[0].body)
    duplicate = client.post(
        "/registrieren/",
        {"first_name": "Erika", "last_name": "Muster", "email": "new@example.test", "password": "Safe-Test-Password-123!"},
    )
    assert duplicate.status_code == 202


@pytest.mark.django_db
@override_settings(
    ALLOWED_HOSTS=["attacker.example.test"],
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    WAGTAILADMIN_BASE_URL="https://5e.klassid.de",
)
def test_registration_email_uses_canonical_public_url_not_request_host(client):
    response = client.post(
        "/registrieren/",
        {
            "first_name": "Erika",
            "last_name": "Muster",
            "email": "canonical@example.test",
            "password": "Safe-Test-Password-123!",
        },
        HTTP_HOST="attacker.example.test",
    )
    assert response.status_code == 202
    assert "https://5e.klassid.de/registrieren/email/" in mail.outbox[0].body
    assert "attacker.example.test" not in mail.outbox[0].body


@pytest.mark.django_db
def test_notifications_are_personal_revision_idempotent_and_read_individually(client, guardian, school_class):
    other = type(guardian).objects.create_user(email="other@example.test", password="Safe-Test-Password-123!")
    Person.objects.create(user=other, first_name="Andere", last_name="Person")
    mine = UserNotification.objects.create(user=guardian, school_class=school_class, category="calendar", object_type="event", object_id="1", revision="v1", title="Neuer Termin", target_url="/kalender/")
    UserNotification.objects.create(user=other, school_class=school_class, category="calendar", object_type="event", object_id="1", revision="v1", title="Fremd", target_url="/kalender/")
    with pytest.raises(IntegrityError), transaction.atomic():
        UserNotification.objects.create(user=guardian, school_class=school_class, category="calendar", object_type="event", object_id="1", revision="v1", title="Doppelt", target_url="/kalender/")
    client.force_login(guardian)
    response = client.post(f"/benachrichtigungen/{mine.pk}/lesen/")
    assert response.status_code == 302
    mine.refresh_from_db()
    assert mine.read_at
    assert UserNotification.objects.filter(user=other, read_at__isnull=True).count() == 1


@pytest.mark.django_db
def test_contact_page_never_contains_unshared_fields_or_other_class(client, guardian, school_class):
    PortalModuleOverride.objects.create(
        module=PortalModule.objects.get(key="contacts"),
        school_class=school_class,
        enabled=True,
    )
    guardian.person.phone = "+49 000 synthetic"
    guardian.person.phone_visibility = "hidden"
    guardian.person.email_visibility = "hidden"
    guardian.person.save()
    other_school = School.objects.create(name="Andere Schule")
    other_year = SchoolYear.objects.create(label="2026/27-other", starts_on=date(2026, 8, 1), ends_on=date(2027, 7, 31))
    other_class = SchoolClass.objects.create(school=other_school, school_year=other_year, name="5a", code="5a")
    outsider = type(guardian).objects.create_user(email="outsider@example.test", password="Safe-Test-Password-123!")
    outsider_person = Person.objects.create(user=outsider, first_name="Nicht", last_name="Sichtbar", phone="secret-phone", phone_visibility="members")
    ClassMembership.objects.create(school_class=other_class, person=outsider_person, valid_from=date(2026, 8, 1))
    client.force_login(guardian)
    response = client.get("/kontakte/")
    body = response.content.decode()
    assert "+49 000 synthetic" not in body
    assert "guardian@example.test" not in body
    assert "secret-phone" not in body
    assert "Nicht Sichtbar" not in body


@pytest.mark.django_db
def test_push_subscription_requires_endpoint_and_keys(client, guardian):
    client.force_login(guardian)
    assert client.post("/push/subscriptions/", data=json.dumps({}), content_type="application/json").status_code == 400
    response = client.post(
        "/push/subscriptions/",
        data=json.dumps({"endpoint": "https://push.example.test/one", "keys": {}}),
        content_type="application/json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_push_subscription_is_per_device_reactivatable_and_not_transferable(client, guardian):
    payload = {
        "endpoint": "https://push.example.test/device-one",
        "keys": {"p256dh": "public-key", "auth": "auth-key"},
        "device_label": "Mein Smartphone mit einem bewusst viel zu langen Gerätenamen" * 3,
    }
    client.force_login(guardian)
    assert client.post("/push/subscriptions/", data=json.dumps(payload), content_type="application/json").status_code == 201
    stored = PushSubscription.objects.get(user=guardian)
    assert len(stored.device_label) == 80
    assert client.delete("/push/subscriptions/", data=json.dumps({"endpoint": payload["endpoint"]}), content_type="application/json").json() == {"removed": True}
    stored.refresh_from_db()
    assert not stored.enabled
    assert client.post("/push/subscriptions/", data=json.dumps(payload), content_type="application/json").status_code == 201
    stored.refresh_from_db()
    assert stored.enabled

    other = type(guardian).objects.create_user(email="push-other@example.test", password="Safe-Test-Password-123!")
    Person.objects.create(user=other, first_name="Push", last_name="Other")
    client.force_login(other)
    assert client.post("/push/subscriptions/", data=json.dumps(payload), content_type="application/json").status_code == 409
    assert client.delete("/push/subscriptions/", data=json.dumps({"endpoint": payload["endpoint"]}), content_type="application/json").json() == {"removed": False}
    stored.refresh_from_db()
    assert stored.user == guardian and stored.enabled


@pytest.mark.django_db
def test_push_self_test_only_targets_selected_owned_device(client, guardian):
    first, _ = PushSubscription.from_values(
        guardian, "https://push.example.test/first", "abc", "def", "Smartphone"
    )
    second, _ = PushSubscription.from_values(
        guardian, "https://push.example.test/second", "ghi", "jkl", "Tablet"
    )
    sender = Mock()
    sender.send.return_value = DeliveryResult(DeliveryStatus.DELIVERED)
    client.force_login(guardian)
    cache.clear()
    with patch("klasse5e.webuntis.notifications.configured_sender", return_value=sender):
        response = client.post("/push/self-test/", {"subscription_id": second.pk})
    assert response.json()["status"] == "delivered"
    assert sender.send.call_count == 1
    assert sender.send.call_args.args[0].endpoint == second.endpoint
    assert sender.send.call_args.args[0].endpoint != first.endpoint

    other = type(guardian).objects.create_user(
        email="push-owner-two@example.test", password="Safe-Test-Password-123!"
    )
    Person.objects.create(user=other, first_name="Andere", last_name="Person")
    foreign, _ = PushSubscription.from_values(
        other, "https://push.example.test/foreign", "mno", "pqr", "Fremdgerät"
    )
    with patch("klasse5e.webuntis.notifications.configured_sender", return_value=sender):
        response = client.post("/push/self-test/", {"subscription_id": foreign.pk})
    assert response.status_code == 409
    assert sender.send.call_count == 1


@pytest.mark.django_db
def test_push_self_test_handles_stale_failure_and_rate_limit(client, guardian):
    stored, _ = PushSubscription.from_values(
        guardian, "https://push.example.test/stale", "stu", "vwx", "Alter Browser"
    )
    sender = Mock()
    sender.send.return_value = DeliveryResult(DeliveryStatus.STALE)
    client.force_login(guardian)
    cache.clear()
    with patch("klasse5e.webuntis.notifications.configured_sender", return_value=sender):
        response = client.post("/push/self-test/", {"subscription_id": stored.pk})
    assert response.json()["status"] == "stale"
    assert not PushSubscription.objects.filter(pk=stored.pk).exists()

    active, _ = PushSubscription.from_values(
        guardian, "https://push.example.test/rate", "yz0", "abc", "Aktiv"
    )
    sender.send.return_value = DeliveryResult(DeliveryStatus.TEMPORARY_FAILURE)
    cache.clear()
    with patch("klasse5e.webuntis.notifications.configured_sender", return_value=sender):
        for _ in range(3):
            assert client.post("/push/self-test/", {"subscription_id": active.pk}).status_code == 200
        limited = client.post("/push/self-test/", {"subscription_id": active.pk})
    assert limited.status_code == 429
    assert limited.json()["status"] == "rate_limited"


@pytest.mark.django_db
def test_settings_navigation_shows_admin_link_only_to_authorized_admins(client, guardian, admin_user):
    client.force_login(guardian)
    guardian_page = client.get("/einstellungen/profil/").content.decode()
    assert "Benachrichtigungen &amp; App" in guardian_page
    assert "Portal verwalten" not in guardian_page

    client.force_login(admin_user)
    admin_page = client.get("/einstellungen/profil/").content.decode()
    assert "Benachrichtigungen &amp; App" in admin_page
    assert "Portal verwalten" in admin_page
