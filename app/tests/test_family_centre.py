from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from klasse5e.core.models import ChildJoinRequest, GuardianChildRelationship, Person


@pytest.fixture
def managed_child(guardian, school_class):
    child = Person.objects.create(first_name="Mila", last_name="Beispiel")
    GuardianChildRelationship.objects.create(
        guardian_person=guardian.person,
        student_person=child,
        relationship_type="mother",
        is_legal_guardian=True,
        may_view_student_profile=True,
        may_manage_profile=True,
        valid_from=timezone.localdate() - timedelta(days=1),
        status="verified",
        verified_by=guardian,
        verified_at=timezone.now(),
    )
    return child


@pytest.mark.django_db
def test_family_centre_shows_parent_and_managed_child(client, guardian, managed_child):
    client.force_login(guardian)

    response = client.get(reverse("ui-family"))

    assert response.status_code == 200
    assert "Familien-Zentrale" in response.content.decode()
    assert "Alex Beispiel" in response.content.decode()
    assert "Mila Beispiel" in response.content.decode()


@pytest.mark.django_db
def test_family_centre_saves_only_the_guardians_own_profile(client, guardian, managed_child):
    client.force_login(guardian)
    person_id = guardian.person.pk

    response = client.post(reverse("ui-family"), {
        "action": "profile", "person_id": person_id,
        f"person-{person_id}-first_name": "Alex", f"person-{person_id}-last_name": "Beispiel",
        f"person-{person_id}-street": "Musterstraße 1", f"person-{person_id}-postal_code": "38440",
        f"person-{person_id}-city": "Wolfsburg", f"person-{person_id}-contact_email": "alex@example.test",
        f"person-{person_id}-phone": "05361 1", f"person-{person_id}-chat_display_name": "Alex",
        "share_phone": "on", "avatar_seed": "v2:1:2:3:4:1:2", "profile_image_mode": "avatar",
    })

    assert response.status_code == 302
    guardian.person.refresh_from_db()
    managed_child.refresh_from_db()
    assert guardian.person.street == "Musterstraße 1"
    assert guardian.person.phone_visibility == "members"
    assert guardian.person.avatar_seed == "v2:1:2:3:4:1:2"
    assert managed_child.street == ""


@pytest.mark.django_db
def test_family_centre_creates_a_pending_child_request(client, guardian, school_class):
    client.force_login(guardian)

    response = client.post(reverse("ui-family"), {
        "action": "add_child", "first_name": "Marie", "last_name": "Beispiel",
        "school_class": school_class.pk,
    })

    assert response.status_code == 302
    assert ChildJoinRequest.objects.filter(guardian=guardian.person, first_name="Marie").exists()
