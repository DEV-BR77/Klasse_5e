import pytest
from allauth.mfa.models import Authenticator
from django.utils import timezone

from klasse5e.chat.models import ChatMessage
from klasse5e.core.models import OnboardingState, PilotReport, RoleAssignment
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
