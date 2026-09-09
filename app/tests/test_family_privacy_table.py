from datetime import timedelta

import pytest
from django.utils import timezone

from klasse5e.core.models import (
    ConsentDecision,
    ConsentTextVersion,
    ConsentType,
    GuardianChildRelationship,
    Person,
)

pytestmark = pytest.mark.django_db


def test_child_privacy_toggles_save_together_without_javascript(client, guardian):
    child = Person.objects.create(first_name="Testkind", last_name="Beispiel")
    relation = GuardianChildRelationship.objects.create(
        guardian_person=guardian.person, student_person=child, relationship_type="mother",
        is_legal_guardian=True, status="verified", verified_by=guardian, verified_at=timezone.now(),
        valid_from=timezone.localdate() - timedelta(days=1), may_view_student_profile=True,
        may_manage_profile=False, may_manage_general_consents=True,
    )
    consent = ConsentType.objects.create(key="test_optional", label="Testfreigabe", category="general", purpose="Testzweck")
    ConsentTextVersion.objects.create(consent_type=consent, version="1", text="Konkrete Testbedingungen", effective_from=timezone.now())
    client.force_login(guardian)
    from django.urls import reverse
    url = f"{reverse('ui-family')}?tab=privacy&child={relation.pk}"
    response = client.get(url, secure=True)
    assert response.status_code == 200
    assert b'<table class="consent-table">' not in response.content
    assert response.content.count(b"Freigaben speichern") == 1
    assert b'name="consent_test_optional"' in response.content
    assert b"Konkrete Testbedingungen" in response.content
    response = client.post(url, {"action": "consents", "person_id": child.pk,
        "consent_test_optional": "on", "tab": "privacy", "child": relation.pk}, secure=True)
    assert response.status_code == 302
    assert ConsentDecision.objects.filter(
        subject_person=child, consent_type=consent
    ).latest("id").decision == "granted"
    response = client.post(url, {"action": "consents", "person_id": child.pk,
        "tab": "privacy", "child": relation.pk}, secure=True)
    assert response.status_code == 302
    assert ConsentDecision.objects.filter(
        subject_person=child, consent_type=consent
    ).latest("id").decision == "revoked"
    relation.may_manage_general_consents = False
    relation.save()
    assert client.post(url, {"action": "consents", "person_id": child.pk,
        "consent_test_optional": "on"}, secure=True).status_code == 403
    assert ConsentDecision.objects.filter(
        subject_person=child, consent_type=consent
    ).count() == 2
