from datetime import date

import pytest
from django.core.exceptions import PermissionDenied
from django.test import override_settings
from django.utils import timezone

from klasse5e.core.models import (
    ConsentDecision,
    ConsentTextVersion,
    ConsentType,
    GuardianChildRelationship,
    OnboardingState,
    Person,
    PushPreference,
    RelationshipStatus,
    StudentProfile,
    TutorialState,
    UserAccount,
)
from klasse5e.core.onboarding import (
    current_policy_version,
    record_decision,
    withdraw_decision,
)
from klasse5e.core.policies import consent_state


@pytest.fixture(autouse=True)
def test_security_settings(settings):
    settings.SECURE_SSL_REDIRECT = False
    settings.STORAGES = {
        **settings.STORAGES,
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }


def verified(user):
    user.email_verified_at = timezone.now()
    user.save(update_fields=["email_verified_at"])
    return user


def child():
    person = Person.objects.create(first_name="Kim", last_name="Testkind")
    StudentProfile.objects.create(person=person)
    return person


def relationship(guardian, student, *, status=RelationshipStatus.VERIFIED, **rights):
    values = {
        "guardian_person": guardian.person,
        "student_person": student,
        "relationship_type": "guardian",
        "is_legal_guardian": True,
        "valid_from": date(2026, 8, 1),
        "status": status,
        "verified_at": timezone.now() if status == RelationshipStatus.VERIFIED else None,
        "may_manage_general_consents": True,
        "may_manage_photo_consents": True,
        "may_manage_biometric_consents": True,
    }
    values.update(rights)
    return GuardianChildRelationship.objects.create(**values)


@pytest.mark.django_db
def test_verified_new_guardian_is_sent_to_resumable_onboarding(client, guardian):
    verified(guardian)
    client.force_login(guardian)
    response = client.get("/mehr/")
    assert response.status_code == 302
    assert response.url == "/onboarding/"
    page = client.get(response.url)
    assert page.status_code == 200
    assert "Schritt 1 von 10" in page.content.decode()


@pytest.mark.django_db
def test_unverified_relationship_cannot_decide_for_child(guardian):
    student = child()
    relationship(guardian, student, status=RelationshipStatus.PENDING)
    with pytest.raises(PermissionDenied):
        record_decision(
            user=guardian,
            subject=student,
            key="photo_gallery",
            decision=ConsentDecision.Decision.GRANTED,
        )


@pytest.mark.django_db
def test_all_current_guardians_must_grant_and_withdrawal_dominates(guardian):
    student = child()
    relationship(guardian, student)
    other = UserAccount.objects.create_user("other@example.test", "Test-Password-123!")
    Person.objects.create(user=other, first_name="Sam", last_name="Beispiel")
    relationship(other, student)
    consent_type = ConsentType.objects.get(key="photo_gallery")

    record_decision(
        user=guardian,
        subject=student,
        key=consent_type.key,
        decision=ConsentDecision.Decision.GRANTED,
    )
    assert consent_state(consent_type, student) == "not_allowed"
    record_decision(
        user=other,
        subject=student,
        key=consent_type.key,
        decision=ConsentDecision.Decision.GRANTED,
    )
    assert consent_state(consent_type, student) == "allowed"
    withdraw_decision(user=other, subject=student, key=consent_type.key)
    assert consent_state(consent_type, student) == "not_allowed"


@pytest.mark.django_db
def test_partial_choices_and_denial_are_not_preselected(client, guardian):
    verified(guardian)
    OnboardingState.objects.create(user=guardian, current_step=7)
    client.force_login(guardian)
    response = client.get("/onboarding/schritt/7/")
    html = response.content.decode()
    assert response.status_code == 200
    assert "checked" not in html
    response = client.post(
        "/onboarding/schritt/7/",
        {
            "subject": guardian.person.id,
            "push_general": "granted",
            "push_chat": "denied",
            "push_events": "denied",
        },
    )
    assert response.status_code == 302
    assert PushPreference.objects.get(user=guardian, key="push_general").enabled
    assert not PushPreference.objects.get(user=guardian, key="push_chat").enabled


@pytest.mark.django_db
@override_settings(BIOMETRIC_SEARCH_ENABLED=False)
def test_biometrics_cannot_be_granted_while_global_gate_is_closed(guardian):
    with pytest.raises(PermissionDenied):
        record_decision(
            user=guardian,
            subject=guardian.person,
            key="biometric_face_search",
            decision=ConsentDecision.Decision.GRANTED,
        )


@pytest.mark.django_db
def test_material_text_change_requires_reonboarding(client, guardian):
    verified(guardian)
    state = OnboardingState.objects.create(
        user=guardian,
        current_step=10,
        completed_at=timezone.now(),
        completed_policy_version=current_policy_version(),
    )
    client.force_login(guardian)
    assert client.get("/mehr/").status_code == 200
    consent_type = ConsentType.objects.get(key="push_general")
    ConsentTextVersion.objects.create(
        consent_type=consent_type,
        version="push-v2-test",
        text="Synthetische neue Testversion.",
        effective_from=timezone.now(),
    )
    state.refresh_from_db()
    response = client.get("/mehr/")
    assert response.status_code == 302
    assert response.url == "/onboarding/"


@pytest.mark.django_db
def test_tutorial_can_be_dismissed_and_restarted(client, guardian):
    client.force_login(guardian)
    response = client.post("/tutorial/schritt/1/", {"action": "dismiss"})
    assert response.status_code == 302
    assert TutorialState.objects.get(user=guardian).dismissed_at is not None
    response = client.post("/tutorial/schritt/1/", {"action": "restart"})
    state = TutorialState.objects.get(user=guardian)
    assert response.url == "/tutorial/schritt/1/"
    assert state.current_step == 1 and state.dismissed_at is None


@pytest.mark.django_db
def test_privacy_page_is_public_and_contains_no_tracking(client):
    response = client.get("/datenschutz/")
    html = response.content.decode()
    assert response.status_code == 200
    assert "Einwilligungen bleiben unter deiner Kontrolle" in html
    assert 'class="privacy-principle"' in html
    assert 'class="choice-card"' not in html
    assert "google-analytics" not in html.casefold()


def test_responsive_styles_cover_mobile_zoom_and_forced_colors(settings):
    css = (settings.BASE_DIR / "static" / "onboarding.css").read_text(encoding="utf-8")
    assert "max-width:24rem" in css
    assert "min-width:48rem" in css
    assert "forced-colors:active" in css
    assert "width:min(100%,46rem)" in css
