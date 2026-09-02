from datetime import date, time, timedelta

import pytest
from allauth.mfa.models import Authenticator
from django.utils import timezone

from klasse5e.core.models import (
    ClassMembership,
    GuardianChildRelationship,
    Person,
    RoleAssignment,
    School,
    SchoolClass,
    StudentProfile,
    UserAccount,
)
from klasse5e.mobility.models import (
    MobilityListing,
    MobilityListingView,
    MobilityReaction,
    PickupDisclosure,
)


def verify_guardian(user, school_class, suffix="child"):
    child = Person.objects.create(first_name="Kind", last_name=suffix)
    StudentProfile.objects.create(person=child)
    ClassMembership.objects.create(
        person=child, school_class=school_class, valid_from=date(2026, 8, 1)
    )
    GuardianChildRelationship.objects.create(
        guardian_person=user.person,
        student_person=child,
        relationship_type="guardian",
        is_legal_guardian=True,
        status="verified",
        verified_at=timezone.now(),
        valid_from=date(2026, 8, 1),
    )
    return child


def make_listing(guardian, school_class, **overrides):
    values = {
        "school_class": school_class,
        "creator": guardian,
        "kind": "offer",
        "transport": "car",
        "direction": "to_school",
        "title": "Zwei Plätze am Morgen",
        "approximate_area": "Nordwest",
        "weekdays": ["mo", "we"],
        "time_from": time(7, 20),
        "time_until": time(7, 45),
        "seats": 2,
        "valid_until": timezone.localdate() + timedelta(days=20),
        "safety_confirmed": True,
    }
    values.update(overrides)
    return MobilityListing.objects.create(**values)


@pytest.mark.django_db
def test_only_verified_guardian_can_open_and_create(client, guardian, school_class):
    client.force_login(guardian)
    assert client.get("/mehr/mobilitaet/").status_code == 404
    verify_guardian(guardian, school_class)
    assert client.get("/mehr/mobilitaet/").status_code == 200
    response = client.post(
        "/mehr/mobilitaet/",
        {
            "kind": "offer",
            "transport": "bicycle",
            "direction": "to_school",
            "title": "Fahrradgruppe Nord",
            "approximate_area": "Nord",
            "weekdays": ["mo", "tu", "we"],
            "time_from": "07:30",
            "time_until": "07:50",
            "seats": "0",
            "valid_until": str(timezone.localdate() + timedelta(days=30)),
            "safety_confirmed": "on",
        },
    )
    assert response.status_code == 302
    assert MobilityListing.objects.get().creator == guardian


@pytest.mark.django_db
def test_listing_and_reaction_are_class_isolated(client, guardian, school_class, year):
    verify_guardian(guardian, school_class)
    listing = make_listing(guardian, school_class)
    other_school = School.objects.create(name="Andere Schule", slug="andere-schule")
    other_class = SchoolClass.objects.create(
        school=other_school, school_year=year, name="6a", code="6a"
    )
    outsider = UserAccount.objects.create_user("outside@example.test", "Safe-Test-Password-123!")
    Person.objects.create(user=outsider, first_name="Andere", last_name="Person")
    ClassMembership.objects.create(
        person=outsider.person, school_class=other_class, valid_from=date(2026, 8, 1)
    )
    verify_guardian(outsider, other_class, "outside-child")
    client.force_login(outsider)
    assert client.get(f"/mehr/mobilitaet/{listing.public_id}/").status_code == 404
    assert (
        client.post(
            f"/mehr/mobilitaet/{listing.public_id}/reagieren/", {"kind": "interested"}
        ).status_code
        == 404
    )


@pytest.mark.django_db
def test_reaction_acceptance_and_private_pickup_lifecycle(client, guardian, school_class):
    verify_guardian(guardian, school_class)
    interested = UserAccount.objects.create_user(
        "interested@example.test", "Safe-Test-Password-123!"
    )
    Person.objects.create(user=interested, first_name="Sam", last_name="Beispiel")
    ClassMembership.objects.create(
        person=interested.person, school_class=school_class, valid_from=date(2026, 8, 1)
    )
    verify_guardian(interested, school_class, "second-child")
    listing = make_listing(guardian, school_class)
    client.force_login(interested)
    assert (
        client.post(
            f"/mehr/mobilitaet/{listing.public_id}/reagieren/",
            {"kind": "interested", "message": "Passt gut"},
        ).status_code
        == 302
    )
    reaction = MobilityReaction.objects.get()
    client.force_login(guardian)
    assert (
        client.post(
            f"/mobility/reactions/{reaction.id}/decision/", {"decision": "accepted"}
        ).status_code
        == 302
    )
    reaction.refresh_from_db()
    assert reaction.status == "accepted"
    assert (
        client.post(
            f"/mobility/reactions/{reaction.id}/pickup/", {"exact_address": "Private Teststraße 9"}
        ).status_code
        == 302
    )
    disclosure = PickupDisclosure.objects.get()
    assert "Private Teststraße 9" not in disclosure.encrypted_address
    client.force_login(interested)
    page = client.get(f"/mehr/mobilitaet/{listing.public_id}/")
    assert "Private Teststraße 9" in page.content.decode()
    client.force_login(guardian)
    assert client.post(f"/mobility/pickups/{disclosure.id}/revoke/").status_code == 302
    disclosure.refresh_from_db()
    assert disclosure.encrypted_address == "" and disclosure.revoked_at is not None


@pytest.mark.django_db
def test_daily_view_is_deduplicated_and_owner_does_not_count(client, guardian, school_class):
    verify_guardian(guardian, school_class)
    viewer = UserAccount.objects.create_user("viewer@example.test", "Safe-Test-Password-123!")
    Person.objects.create(user=viewer, first_name="View", last_name="Person")
    ClassMembership.objects.create(
        person=viewer.person, school_class=school_class, valid_from=date(2026, 8, 1)
    )
    verify_guardian(viewer, school_class, "view-child")
    listing = make_listing(guardian, school_class)
    client.force_login(guardian)
    client.get(f"/mehr/mobilitaet/{listing.public_id}/")
    assert MobilityListingView.objects.count() == 0
    client.force_login(viewer)
    client.get(f"/mehr/mobilitaet/{listing.public_id}/")
    client.get(f"/mehr/mobilitaet/{listing.public_id}/")
    assert MobilityListingView.objects.count() == 1


@pytest.mark.django_db
def test_moderator_can_pause_listing(client, guardian, school_class):
    verify_guardian(guardian, school_class)
    listing = make_listing(guardian, school_class)
    moderator = UserAccount.objects.create_user(
        "moderator-mobility@example.test", "Safe-Test-Password-123!"
    )
    Person.objects.create(user=moderator, first_name="Mod", last_name="Person")
    ClassMembership.objects.create(
        person=moderator.person, school_class=school_class, valid_from=date(2026, 8, 1)
    )
    verify_guardian(moderator, school_class, "mod-child")
    RoleAssignment.objects.create(user=moderator, school_class=school_class, role="moderator")
    Authenticator.objects.create(
        user=moderator,
        type=Authenticator.Type.TOTP,
        data={"secret": "synthetic-test-only"},
    )
    client.force_login(moderator)
    response = client.post(f"/mehr/mobilitaet/{listing.public_id}/moderieren/", {"action": "pause"})
    assert response.status_code == 302
    listing.refresh_from_db()
    assert listing.status == "paused"
