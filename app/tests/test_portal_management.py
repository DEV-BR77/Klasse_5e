from datetime import date

import pytest
from allauth.mfa.models import Authenticator
from django.utils import timezone

from klasse5e.chat.models import ChatMessage
from klasse5e.core.models import (
    ClassMembership,
    GuardianChildRelationship,
    OnboardingState,
    Person,
    PilotReport,
    RoleAssignment,
    StudentProfile,
)
from klasse5e.core.onboarding import current_policy_version


@pytest.mark.django_db
def test_management_and_qr_are_hidden_from_guardians(client, guardian, admin_user):
    client.force_login(guardian)
    assert client.get("/verwaltung/", secure=True).status_code == 404
    assert client.get("/verwaltung/anmeldung/qr.svg", secure=True).status_code == 404

    client.force_login(admin_user)
    assert client.get("/verwaltung/", secure=True).status_code == 200
    qr = client.get("/verwaltung/anmeldung/qr.svg", secure=True)
    assert qr.status_code == 200
    assert qr["Content-Type"] == "image/svg+xml"
    assert b"<svg" in qr.content


@pytest.mark.django_db
def test_pilot_report_records_page_without_exposing_github(client, guardian):
    client.force_login(guardian)
    response = client.post(
        "/pilot/melden/",
        {"kind": "bug", "description": "Schaltfläche reagiert nicht", "page_path": "/kalender/?ansicht=day"},
        secure=True,
    )
    assert response.status_code == 302
    report = PilotReport.objects.get()
    assert report.reporter == guardian
    assert report.page_path == "/kalender/?ansicht=day"


@pytest.mark.django_db
def test_class_admin_can_create_chat_room_and_event(client, guardian, school_class):
    RoleAssignment.objects.filter(user=guardian).update(role="class_admin")
    guardian.email_verified_at = timezone.now()
    guardian.save(update_fields=["email_verified_at"])
    OnboardingState.objects.create(
        user=guardian,
        current_step=10,
        completed_at=timezone.now(),
        completed_policy_version=current_policy_version(),
    )
    Authenticator.objects.create(
        user=guardian,
        type=Authenticator.Type.TOTP,
        data={"secret": "synthetic-test-only"},
    )
    client.force_login(guardian)
    response = client.post("/chat/", {"title": "Elternabend"}, secure=True)
    assert response.status_code == 302
    room = school_class.chatroom_set.get()
    assert room.title == "Elternabend"
    ChatMessage.objects.create(room=room, author=guardian, body="Willkommen")
    room_page = client.get(f"/chat/{room.public_id}/ansicht/", secure=True)
    assert b"Willkommen" in room_page.content
    assert b"ChatMessage object" not in room_page.content

    response = client.post(
        "/mehr/veranstaltungen/",
        {
            "title": "Klassenfest",
            "description": "Gemeinsames Fest",
            "location": "Schulhof",
            "starts_at": "2026-09-10T15:00",
            "ends_at": "2026-09-10T18:00",
        },
        secure=True,
    )
    assert response.status_code == 302
    assert school_class.event_set.get().title == "Klassenfest"


@pytest.mark.django_db
@pytest.mark.parametrize("appearance", ["standard", "classic", "modern", "math"])
def test_new_chat_with_no_automatic_deletion(client, admin_user, school_class, appearance):
    from klasse5e.chat.models import ChatRoom

    client.force_login(admin_user)
    response = client.post("/chat/", {
        "title": "Neuer Testraum", "appearance": appearance, "retention_category": "",
    }, secure=True)
    assert response.status_code == 302
    room = ChatRoom.objects.get(school_class=school_class, title="Neuer Testraum")
    assert room.appearance == appearance
    assert room.retention_category is None


@pytest.mark.django_db
def test_new_chat_rejects_invalid_retention_without_server_error(client, admin_user, school_class):
    from klasse5e.chat.models import ChatRoom

    client.force_login(admin_user)
    response = client.post("/chat/", {
        "title": "Invalid retention", "appearance": "modern", "retention_category": "invalid",
    }, secure=True)
    assert response.status_code == 302
    assert not ChatRoom.objects.filter(school_class=school_class, title="Invalid retention").exists()


@pytest.mark.django_db
def test_admin_can_delete_a_chat_room_and_room_uses_selected_appearance(
    client, admin_user, school_class
):
    from klasse5e.chat.models import ChatRoom

    client.force_login(admin_user)
    room = ChatRoom.objects.create(
        school_class=school_class,
        school_year=school_class.school_year,
        title="Mathe-AG",
        appearance=ChatRoom.Appearance.MATH,
    )

    page = client.get(f"/chat/{room.public_id}/ansicht/", secure=True)
    assert page.status_code == 200
    assert b"chat-room--math" in page.content
    overview = client.get("/chat/", secure=True)
    assert b"L\xc3\xb6schen" in overview.content

    response = client.post("/chat/", {"action": "delete", "room_id": room.public_id}, secure=True)
    assert response.status_code == 302
    assert not ChatRoom.objects.filter(pk=room.pk).exists()


@pytest.mark.django_db
def test_portal_admin_assigns_and_revokes_parent_representative(client, admin_user, guardian, school_class):
    child_person = Person.objects.create(first_name="Kind", last_name="Beispiel")
    StudentProfile.objects.create(person=child_person)
    ClassMembership.objects.create(
        person=child_person, school_class=school_class, valid_from=date(2026, 8, 1)
    )
    GuardianChildRelationship.objects.create(
        guardian_person=guardian.person,
        student_person=child_person,
        relationship_type="guardian",
        is_legal_guardian=True,
        may_view_student_profile=True,
        valid_from=date(2026, 8, 1),
        status="verified",
        verified_by=admin_user,
        verified_at=timezone.now(),
    )
    client.force_login(admin_user)
    response = client.post(
        "/verwaltung/rollen/",
        {
            "action": "assign",
            "role": "parent_representative",
            "user_id": guardian.pk,
            "school_class_id": school_class.pk,
        },
        secure=True,
    )
    assert response.status_code == 302
    assignment = RoleAssignment.objects.get(
        user=guardian, school_class=school_class, role="parent_representative"
    )
    assert assignment.active

    response = client.post(
        "/verwaltung/rollen/", {"action": "revoke", "assignment_id": assignment.pk}, secure=True
    )
    assert response.status_code == 302
    assignment.refresh_from_db()
    assert not assignment.active
