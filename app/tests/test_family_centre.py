from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from klasse5e.core.models import (
    ChildJoinRequest,
    ClassMembership,
    GuardianChildRelationship,
    Household,
    Person,
)


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
def test_family_centre_uses_person_scoped_tabs(client, guardian, managed_child):
    client.force_login(guardian)
    relationship = GuardianChildRelationship.objects.get(student_person=managed_child)

    response = client.get(f"{reverse('ui-family')}?tab=privacy&child={relationship.pk}")

    assert response.status_code == 200
    body = response.content.decode()
    assert 'aria-label="Familien-Zentrale"' in body
    assert "Schulzugänge" in body
    assert "Datenschutz und Einwilligungen" in body


@pytest.mark.django_db
def test_family_centre_saves_only_the_guardians_own_profile(client, guardian, managed_child):
    client.force_login(guardian)
    person_id = guardian.person.pk

    response = client.post(reverse("ui-family"), {
        "action": "profile", "person_id": person_id,
        f"person-{person_id}-first_name": "Alex", f"person-{person_id}-last_name": "Beispiel",
        f"person-{person_id}-street": "Musterstraße 1", f"person-{person_id}-postal_code": "38440",
        f"person-{person_id}-city": "Wolfsburg", f"person-{person_id}-contact_email": "alex@example.test",
        f"person-{person_id}-phone": "05361 123456", f"person-{person_id}-chat_display_name": "Alex",
        "share_phone": "on", "avatar_seed": "v2:1:2:3:4:1:2", "profile_image_mode": "avatar",
    })

    assert response.status_code == 302
    guardian.person.refresh_from_db()
    managed_child.refresh_from_db()
    assert guardian.person.street == "Musterstraße 1"
    assert guardian.person.phone == "+495361123456"
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


@pytest.mark.django_db
def test_child_contact_sharing_uses_the_same_address_switch_as_an_adult(
    client, guardian, managed_child, school_class
):
    relationship = GuardianChildRelationship.objects.get(student_person=managed_child)
    ClassMembership.objects.create(
        person=managed_child, school_class=school_class, valid_from=timezone.localdate()
    )
    client.force_login(guardian)

    page = client.get(f"{reverse('ui-family')}?tab=data&child={relationship.pk}")

    assert page.status_code == 200
    assert page.content.decode().count('class="sharing-toggle"') == 3
    response = client.post(
        reverse("ui-family"),
        {
            "action": "profile",
            "person_id": managed_child.pk,
            "tab": "data",
            "child": relationship.pk,
            f"person-{managed_child.pk}-first_name": "Mila",
            f"person-{managed_child.pk}-last_name": "Beispiel",
            f"person-{managed_child.pk}-street": "Musterstraße 1",
            f"person-{managed_child.pk}-postal_code": "38440",
            f"person-{managed_child.pk}-city": "Wolfsburg",
            f"person-{managed_child.pk}-contact_email": "mila@example.test",
            f"person-{managed_child.pk}-phone": "05361 123456",
            f"person-{managed_child.pk}-chat_display_name": "Mila",
            "share_address": "on",
            "share_phone": "on",
            "share_contact_email": "on",
            "school_class": school_class.pk,
            "avatar_seed": "v2:1:2:3:4:1:2",
            "profile_image_mode": "avatar",
        },
    )

    assert response.status_code == 302
    managed_child.refresh_from_db()
    assert managed_child.field_visibility["street"]
    assert managed_child.field_visibility["postal_code"]
    assert managed_child.field_visibility["city"]
    assert managed_child.phone_visibility == "members"
    assert managed_child.phone == "+495361123456"
    assert managed_child.email_visibility == "members"


@pytest.mark.django_db
def test_contacts_show_one_clean_family_name_and_only_shared_address(
    client, guardian, managed_child, school_class
):
    ClassMembership.objects.create(
        person=managed_child, school_class=school_class, valid_from=timezone.localdate()
    )
    guardian.person.street = "Musterstraße 1"
    guardian.person.postal_code = "38440"
    guardian.person.city = "Wolfsburg"
    guardian.person.field_visibility = {"street": True, "postal_code": True, "city": True}
    guardian.person.phone = "+495361123456"
    guardian.person.phone_visibility = "members"
    guardian.person.email_visibility = "members"
    guardian.person.save()
    managed_child.contact_email = "mila@example.test"
    managed_child.email_visibility = "members"
    managed_child.phone = "+4915123456789"
    managed_child.phone_visibility = "members"
    managed_child.save()
    household = Household.objects.create(label="Familie Beispiel")
    household.members.add(guardian.person)
    client.force_login(guardian)

    response = client.get(reverse("ui-contacts"))

    assert response.status_code == 200
    body = response.content.decode()
    assert "Familie Beispiel" in body
    assert "Familie Familie Beispiel" not in body
    assert "Musterstraße 1 · 38440 Wolfsburg" in body
    assert 'aria-label="Kontaktkarte für Familie Beispiel öffnen"' in body
    assert 'href="tel:+495361123456"' in body
    assert "+49 5361 123456" in body
    assert 'href="mailto:guardian@example.test"' in body
    assert 'href="tel:+4915123456789"' in body
    assert 'href="mailto:mila@example.test"' in body
    assert body.count('class="contact-person"') == 2
    assert "Wähle die Person aus" not in body
    assert 'href="/mehr/mobilitaet/" class="app-bottom-nav__item"' not in body
    assert 'href="/kontakte/" class="app-bottom-nav__item"' in body

    guardian.person.field_visibility["city"] = False
    guardian.person.save(update_fields=["field_visibility"])
    revoked_body = client.get(reverse("ui-contacts")).content.decode()
    assert "Musterstraße 1 · 38440 Wolfsburg" not in revoked_body
