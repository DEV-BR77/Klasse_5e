import re
from datetime import date, timedelta

import pytest
from django.core import mail
from django.db import IntegrityError, transaction
from django.test import override_settings
from django.utils import timezone

from klasse5e.core.models import (
    ActivationGrant,
    ClassMembership,
    Person,
    PortalModule,
    PortalModuleOverride,
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
