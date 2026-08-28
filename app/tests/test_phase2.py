from datetime import date, timedelta

import pytest
from django.contrib.sessions.models import Session
from django.utils import timezone

from klasse5e.core.models import (
    AuditEvent,
    ConsentDecision,
    ConsentTextVersion,
    ConsentType,
    GuardianChildRelationship,
    Household,
    Invitation,
    Person,
    Role,
    RoleAssignment,
    StudentProfile,
    UserAccount,
)
from klasse5e.core.policies import (
    active_roles,
    consent_state,
    has_active_membership,
    may_view_student,
)


@pytest.mark.django_db
def test_no_public_registration(client):
    response = client.post(
        "/accounts/signup/",
        {
            "email": "public@example.test",
            "password1": "Safe-New-Password-123!",
            "password2": "Safe-New-Password-123!",
        },
    )
    assert response.status_code in {200, 403, 404}
    assert not UserAccount.objects.filter(email="public@example.test").exists()


@pytest.mark.django_db
def test_invitation_is_hashed_single_use_and_expires(client, admin_user):
    invitation, token = Invitation.issue("new@example.test", admin_user)
    assert token not in invitation.token_hash
    response = client.post(f"/invitation/{token}/", {"password": "Safe-New-Password-123!"})
    assert response.status_code == 302
    assert (
        client.post(f"/invitation/{token}/", {"password": "Safe-New-Password-123!"}).status_code
        == 410
    )
    expired, expired_token = Invitation.issue(
        "late@example.test", admin_user, timedelta(seconds=-1)
    )
    assert (
        client.post(
            f"/invitation/{expired_token}/", {"password": "Safe-New-Password-123!"}
        ).status_code
        == 410
    )


@pytest.mark.django_db
def test_separate_guardians_multiple_children_and_households(school_class):
    guardians = [
        Person.objects.create(first_name=f"Guardian{i}", last_name="Synthetic") for i in range(2)
    ]
    students = []
    for index in range(2):
        person = Person.objects.create(first_name=f"Student{index}", last_name="Synthetic")
        StudentProfile.objects.create(person=person)
        students.append(person)
    Household.objects.create(label="Household A").members.add(guardians[0], students[0])
    Household.objects.create(label="Household B").members.add(
        guardians[1], students[0], students[1]
    )
    for guardian in guardians:
        GuardianChildRelationship.objects.create(
            guardian_person=guardian,
            student_person=students[0],
            relationship_type="guardian",
            valid_from=date(2026, 8, 1),
            status="verified",
            verified_at=timezone.now(),
            may_view_student_profile=True,
        )
    assert StudentProfile.objects.filter(person__user__isnull=True).count() == 2
    assert students[0].student_relationships.count() == 2
    assert guardians[1].guardian_relationships.count() == 1


@pytest.mark.django_db
def test_relationship_must_be_verified_current_and_explicit(guardian):
    student_person = Person.objects.create(first_name="Sam", last_name="Synthetic")
    student = StudentProfile.objects.create(person=student_person)
    relationship = GuardianChildRelationship.objects.create(
        guardian_person=guardian.person,
        student_person=student_person,
        relationship_type="other",
        valid_from=date(2026, 8, 1),
        status="pending",
        may_view_student_profile=True,
    )
    assert not may_view_student(guardian, student)
    relationship.status = "verified"
    relationship.verified_at = timezone.now()
    relationship.valid_until = date(2026, 8, 23)
    relationship.save()
    assert not may_view_student(guardian, student)


@pytest.mark.django_db
def test_membership_and_class_role_isolation(guardian, school_class, year):
    assert has_active_membership(guardian, school_class)
    other = type(school_class).objects.create(name="Other", school_year=year)
    assert not has_active_membership(guardian, other)
    assert active_roles(guardian, school_class) == {Role.GUARDIAN}
    assert active_roles(guardian, other) == set()


@pytest.mark.django_db
def test_primary_and_deputy_roles_are_distinct(admin_user):
    deputy = UserAccount.objects.create_user(email="deputy@example.test")
    RoleAssignment.objects.create(user=deputy, role=Role.DEPUTY_ADMIN)
    assert Role.PRIMARY_ADMIN in active_roles(admin_user)
    assert Role.PRIMARY_ADMIN not in active_roles(deputy)


@pytest.mark.django_db
def test_contact_visibility_defaults_hidden():
    person = Person.objects.create(first_name="Private", last_name="Person", phone="000")
    assert person.email_visibility == "hidden"
    assert person.phone_visibility == "hidden"


@pytest.mark.django_db
def test_conflicting_and_revoked_consents_are_conservative():
    subject = Person.objects.create(first_name="Subject", last_name="Synthetic")
    people = [
        Person.objects.create(first_name=f"Decider{i}", last_name="Synthetic") for i in range(2)
    ]
    consent_type = ConsentType.objects.create(
        key="biometric-search",
        label="Biometrie",
        category="biometric",
        purpose="Draft",
        recipients="Local service",
    )
    text = ConsentTextVersion.objects.create(
        consent_type=consent_type,
        version="draft-1",
        text="Fachlicher Entwurf",
        effective_from=timezone.now(),
    )
    ConsentDecision.objects.create(
        consent_type=consent_type,
        text_version=text,
        subject_person=subject,
        deciding_person=people[0],
        decision="granted",
    )
    ConsentDecision.objects.create(
        consent_type=consent_type,
        text_version=text,
        subject_person=subject,
        deciding_person=people[1],
        decision="denied",
    )
    assert consent_state(consent_type, subject) == "clarification_required"
    ConsentDecision.objects.create(
        consent_type=consent_type,
        text_version=text,
        subject_person=subject,
        deciding_person=people[1],
        decision="granted",
        revoked_at=timezone.now(),
    )
    assert consent_state(consent_type, subject) == "not_allowed"


@pytest.mark.django_db
def test_privileged_account_requires_mfa(client, db):
    user = UserAccount.objects.create_user(
        email="editor@example.test", password="Safe-Test-Password-123!"
    )
    Person.objects.create(user=user, first_name="Edit", last_name="Synthetic")
    RoleAssignment.objects.create(user=user, role=Role.EDITOR)
    client.force_login(user)
    response = client.get("/")
    assert response.status_code == 302
    assert response.url == "/accounts/2fa/totp/activate/"


@pytest.mark.django_db
def test_session_revocation_and_audit(client, guardian):
    client.force_login(guardian)
    assert Session.objects.exists()
    assert client.post("/sessions/revoke-all/").status_code == 200
    assert not Session.objects.exists()
    assert AuditEvent.objects.filter(action="sessions.revoked_all", actor=guardian).exists()


@pytest.mark.django_db
def test_push_subscribe_and_idempotent_unsubscribe(client, guardian):
    client.force_login(guardian)
    payload = {
        "endpoint": "https://push.example.test/subscription",
        "keys": {"p256dh": "public", "auth": "auth"},
    }
    assert (
        client.post("/push/subscriptions/", payload, content_type="application/json").status_code
        == 201
    )
    assert (
        client.delete("/push/subscriptions/", payload, content_type="application/json").status_code
        == 200
    )
    assert (
        client.delete("/push/subscriptions/", payload, content_type="application/json").status_code
        == 200
    )


def test_pwa_service_worker_caches_only_public_shell(client):
    script = client.get("/service-worker.js").content.decode()
    assert "/offline/" in script and "/static/app.css" in script
    assert "dashboard" not in script and "profile" not in script


@pytest.mark.django_db
def test_disabled_account_loses_access(client, guardian):
    client.force_login(guardian)
    guardian.is_active = False
    guardian.save()
    assert client.get("/").status_code == 302
