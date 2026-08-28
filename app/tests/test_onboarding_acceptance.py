from datetime import date

import pytest
from django.test import override_settings
from django.utils import timezone

from klasse5e.core.models import (
    ConsentDecision,
    ConsentType,
    GuardianChildRelationship,
    OnboardingState,
    Person,
    PushPreference,
    PushSubscription,
    StudentProfile,
    UserAccount,
)
from klasse5e.core.onboarding import record_decision, withdraw_decision
from klasse5e.core.policies import consent_state


@pytest.fixture(autouse=True)
def template_test_settings(settings):
    settings.SECURE_SSL_REDIRECT = False
    settings.STORAGES = {
        **settings.STORAGES,
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }


def make_child():
    person = Person.objects.create(first_name="Robin", last_name="Testkind")
    StudentProfile.objects.create(person=person)
    return person


def relate(user, student):
    return GuardianChildRelationship.objects.create(
        guardian_person=user.person,
        student_person=student,
        relationship_type="guardian",
        is_legal_guardian=True,
        may_view_student_profile=True,
        may_manage_general_consents=True,
        may_manage_photo_consents=True,
        may_manage_biometric_consents=True,
        valid_from=date(2026, 8, 1),
        status="verified",
        verified_at=timezone.now(),
    )


@pytest.mark.django_db
def test_student_login_gets_child_friendly_resumable_flow(client):
    user = UserAccount.objects.create_user("student@example.test", "Test-Password-123!")
    user.email_verified_at = timezone.now()
    user.save(update_fields=["email_verified_at"])
    person = Person.objects.create(user=user, first_name="Robin", last_name="Testkind")
    StudentProfile.objects.create(person=person)
    client.force_login(user)
    response = client.get("/onboarding/")
    assert response.status_code == 200
    assert "Schritt 1 von 10" in response.content.decode()
    assert OnboardingState.objects.get(user=user).current_step == 1


@pytest.mark.django_db
def test_denying_every_optional_purpose_keeps_every_feature_off(guardian):
    for consent_type in ConsentType.objects.all():
        record_decision(
            user=guardian,
            subject=guardian.person,
            key=consent_type.key,
            decision=ConsentDecision.Decision.DENIED,
        )
    assert not ConsentDecision.objects.filter(
        deciding_person=guardian.person, decision=ConsentDecision.Decision.GRANTED
    ).exists()
    assert not PushPreference.objects.filter(user=guardian, enabled=True).exists()


@pytest.mark.django_db
def test_full_push_and_profile_withdrawal_applies_runtime_side_effects(guardian):
    guardian.person.email_visibility = "members"
    guardian.person.phone_visibility = "members"
    guardian.person.save(update_fields=["email_visibility", "phone_visibility"])
    PushSubscription.from_values(
        guardian, "https://push.example.test/synthetic", "public-test-key", "auth-test-key"
    )
    for key in ("profile_contact_visibility", "push_general", "push_chat", "push_events"):
        record_decision(
            user=guardian,
            subject=guardian.person,
            key=key,
            decision=ConsentDecision.Decision.GRANTED,
        )
        withdraw_decision(user=guardian, subject=guardian.person, key=key)
    guardian.person.refresh_from_db()
    assert guardian.person.email_visibility == "hidden"
    assert guardian.person.phone_visibility == "hidden"
    assert not PushPreference.objects.filter(user=guardian, enabled=True).exists()
    assert not PushSubscription.objects.filter(user=guardian, enabled=True).exists()


@pytest.mark.django_db
@override_settings(BIOMETRIC_SEARCH_ENABLED=True)
def test_biometric_pilot_requires_valid_decisions_from_both_guardians(guardian):
    student = make_child()
    relate(guardian, student)
    second = UserAccount.objects.create_user("second@example.test", "Test-Password-123!")
    Person.objects.create(user=second, first_name="Taylor", last_name="Beispiel")
    relate(second, student)
    consent_type = ConsentType.objects.get(key="biometric_face_search")
    record_decision(
        user=guardian,
        subject=student,
        key=consent_type.key,
        decision=ConsentDecision.Decision.GRANTED,
    )
    assert consent_state(consent_type, student) == "not_allowed"
    record_decision(
        user=second,
        subject=student,
        key=consent_type.key,
        decision=ConsentDecision.Decision.GRANTED,
    )
    assert consent_state(consent_type, student) == "allowed"
