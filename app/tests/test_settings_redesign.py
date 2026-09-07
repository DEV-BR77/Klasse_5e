import pytest
from django.urls import reverse
from django.utils import timezone

from klasse5e.core.models import ConsentDecision, OnboardingState


@pytest.mark.django_db
def test_setup_overview_can_be_left_without_granting_consents(client, guardian, settings):
    settings.SECURE_SSL_REDIRECT = False
    guardian.email_verified_at = timezone.now()
    guardian.save(update_fields=["email_verified_at"])
    client.force_login(guardian)
    assert client.get(reverse("ui-more")).url == reverse("onboarding-resume")
    page = client.get(reverse("onboarding-resume"))
    assert "In deinem Tempo startklar" in page.content.decode()
    assert client.get(reverse("ui-more")).status_code == 200
    assert client.get(reverse("personal-profile")).status_code == 200
    assert client.get(reverse("ui-family")).status_code == 200
    assert not OnboardingState.objects.get(user=guardian).completed_at
    assert not ConsentDecision.objects.filter(deciding_person=guardian.person).exists()


@pytest.mark.django_db
def test_pause_preserves_step_and_does_not_trap_user(client, guardian, settings):
    settings.SECURE_SSL_REDIRECT = False
    guardian.email_verified_at = timezone.now()
    guardian.save(update_fields=["email_verified_at"])
    OnboardingState.objects.create(user=guardian, current_step=4)
    client.force_login(guardian)
    response = client.post("/onboarding/schritt/4/", {"action": "pause"})
    assert response.url == reverse("onboarding-paused")
    assert client.get(reverse("ui-more")).status_code == 200
    assert OnboardingState.objects.get(user=guardian).current_step == 4
    assert not ConsentDecision.objects.filter(deciding_person=guardian.person).exists()


@pytest.mark.django_db
def test_preference_form_is_directly_accessible_without_wizard_completion(
    client, guardian, settings
):
    settings.SECURE_SSL_REDIRECT = False
    client.force_login(guardian)
    response = client.get("/onboarding/schritt/7/?mode=settings")
    assert response.status_code == 200
    assert "Änderungen speichern" in response.content.decode()
    assert not OnboardingState.objects.get(user=guardian).completed_at
