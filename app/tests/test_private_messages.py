from datetime import date, timedelta
from unittest.mock import Mock, patch

import pytest
from allauth.mfa.models import Authenticator
from django.utils import timezone
from web_push_kit import DeliveryResult, DeliveryStatus

from klasse5e.chat.models import ChatMessage, ChatReport, DirectConversation
from klasse5e.chat.retention import cleanup_expired_messages
from klasse5e.chat.services import create_message, get_or_create_direct_conversation
from klasse5e.core.models import (
    AuditEvent,
    ClassMembership,
    GuardianChildRelationship,
    Person,
    PortalModule,
    PortalModuleOverride,
    PushPreference,
    PushSubscription,
    RoleAssignment,
    School,
    SchoolClass,
    SchoolYear,
    StudentProfile,
    UserAccount,
    UserNotification,
)


@pytest.fixture
def direct_family(db):
    year = SchoolYear.objects.create(
        label="2026/27-private-chat",
        starts_on=date(2026, 8, 1),
        ends_on=date(2027, 7, 31),
        is_active=True,
    )
    school = School.objects.create(name="Privatchat-Testschule", slug="private-chat-school")
    school_class = SchoolClass.objects.create(
        school=school,
        school_year=year,
        name="Privatchat 5e",
        code="private-5e",
    )
    PortalModuleOverride.objects.create(
        module=PortalModule.objects.get(key="contacts"),
        school_class=school_class,
        enabled=True,
    )

    first = UserAccount.objects.create_user(
        email="first-private@example.test", password="Safe-Test-Password-123!"
    )
    second = UserAccount.objects.create_user(
        email="second-private@example.test", password="Safe-Test-Password-123!"
    )
    first_person = Person.objects.create(
        user=first, first_name="Alex", last_name="Erste Familie"
    )
    second_person = Person.objects.create(
        user=second, first_name="Sam", last_name="Zweite Familie"
    )
    child = Person.objects.create(first_name="Mila", last_name="Kind")
    StudentProfile.objects.create(person=child)
    for person in (first_person, second_person, child):
        ClassMembership.objects.create(
            school_class=school_class,
            person=person,
            valid_from=year.starts_on,
        )
    for guardian in (first_person, second_person):
        GuardianChildRelationship.objects.create(
            guardian_person=guardian,
            student_person=child,
            relationship_type="guardian",
            is_legal_guardian=True,
            may_view_student_profile=True,
            valid_from=year.starts_on,
            status="verified",
            verified_by=first,
            verified_at=timezone.now(),
        )
    return first, second, first_person, second_person, school_class


@pytest.mark.django_db
def test_contact_card_starts_one_conversation_for_the_selected_person(client, direct_family):
    first, second, first_person, second_person, school_class = direct_family
    client.force_login(first)

    contacts = client.get("/kontakte/", secure=True)
    assert contacts.status_code == 200
    assert f'/chat/direkt/{second_person.pk}/starten/'.encode() in contacts.content
    assert "Sam schreiben" in contacts.content.decode()
    assert f'/chat/direkt/{first_person.pk}/starten/'.encode() not in contacts.content

    started = client.post(f"/chat/direkt/{second_person.pk}/starten/", secure=True)
    assert started.status_code == 302
    conversation = DirectConversation.objects.get()
    assert conversation.school_class == school_class
    assert started.url == f"/chat/{conversation.room.public_id}/ansicht/"
    assert conversation.room.retention_category.name == "Private Nachrichten"
    assert conversation.room.retention_category.automatic_deletion_enabled
    assert conversation.room.retention_category.retention_days == 180

    repeated = client.post(f"/chat/direkt/{second_person.pk}/starten/", secure=True)
    client.force_login(second)
    reversed_start = client.post(f"/chat/direkt/{first_person.pk}/starten/", secure=True)
    assert repeated.url == started.url
    assert reversed_start.url == started.url
    assert DirectConversation.objects.count() == 1


@pytest.mark.django_db
def test_only_active_participants_can_read_and_write_direct_conversation(
    client, direct_family
):
    first, second, _first_person, _second_person, school_class = direct_family
    conversation = get_or_create_direct_conversation(first, second.person, school_class)
    room_url = f"/chat/{conversation.room.public_id}/ansicht/"

    client.force_login(first)
    assert client.post(room_url, {"body": "Vertrauliche Testnachricht"}, secure=True).status_code == 302
    client.force_login(second)
    response = client.get(room_url, secure=True)
    assert response.status_code == 200
    assert "Vertrauliche Testnachricht" in response.content.decode()
    assert "Alex" in response.content.decode()

    outsider = UserAccount.objects.create_user(
        email="private-outsider@example.test", password="Safe-Test-Password-123!"
    )
    outsider_person = Person.objects.create(
        user=outsider, first_name="Fremd", last_name="Mitglied"
    )
    ClassMembership.objects.create(
        person=outsider_person,
        school_class=school_class,
        valid_from=school_class.school_year.starts_on,
    )
    RoleAssignment.objects.create(user=outsider, school_class=school_class, role="primary_admin")
    Authenticator.objects.create(
        user=outsider,
        type=Authenticator.Type.TOTP,
        data={"secret": "synthetic-test-only"},
    )
    client.force_login(outsider)
    assert client.get(room_url, secure=True).status_code == 404
    assert client.post(room_url, {"body": "Unbefugt"}, secure=True).status_code == 404

    GuardianChildRelationship.objects.filter(guardian_person=second.person).update(
        status="revoked", valid_until=timezone.localdate()
    )
    second.person.classmembership_set.update(status="ended", valid_until=timezone.localdate())
    client.force_login(second)
    assert client.get(room_url, secure=True).status_code == 404


@pytest.mark.django_db
def test_direct_message_creates_only_neutral_notifications(
    direct_family, django_capture_on_commit_callbacks
):
    first, second, _first_person, _second_person, school_class = direct_family
    conversation = get_or_create_direct_conversation(first, second.person, school_class)
    PushPreference.objects.create(user=second, key="push_chat", enabled=True)
    PushSubscription.from_values(
        second,
        "https://push.example.test/private-device",
        "public-key",
        "auth-key",
        "Testgerät",
    )
    sender = Mock()
    sender.send.return_value = DeliveryResult(DeliveryStatus.DELIVERED)
    body = "Vertraulicher Inhalt nur für Sam"

    with patch("klasse5e.chat.notifications.configured_sender", return_value=sender):
        with django_capture_on_commit_callbacks(execute=True):
            message = create_message(conversation.room, first, body)

    notification = UserNotification.objects.get(user=second)
    assert notification.title == "Neue private Nachricht"
    assert notification.summary == "In deiner privaten Unterhaltung wartet eine neue Nachricht."
    assert body not in notification.title + notification.summary
    assert first.person.first_name not in notification.title + notification.summary
    assert str(conversation.room.public_id) in notification.target_url
    assert not UserNotification.objects.filter(user=first).exists()
    assert sender.send.call_count == 1
    payload = sender.send.call_args.args[1]
    assert payload.body == "Du hast eine neue private Nachricht."
    assert body not in payload.body
    assert payload.message_id == f"direct-{message.public_id}"


@pytest.mark.django_db
def test_reported_direct_message_is_moderated_without_opening_private_thread(
    client, direct_family
):
    first, second, _first_person, _second_person, school_class = direct_family
    conversation = get_or_create_direct_conversation(first, second.person, school_class)
    message = ChatMessage.objects.create(
        room=conversation.room, author=first, body="Gemeldeter Inhalt"
    )
    ChatMessage.objects.filter(pk=message.pk).update(
        created_at=timezone.now() - timedelta(days=181)
    )

    client.force_login(second)
    report_response = client.post(
        f"/chat/messages/{message.public_id}/report/",
        {"reason": "privacy", "return_to": "room"},
        secure=True,
    )
    assert report_response.status_code == 302
    assert ChatReport.objects.filter(message=message, reporter=second, reason="privacy").exists()
    assert AuditEvent.objects.filter(
        action="chat.message.reported", target_id=str(message.public_id)
    ).exists()
    assert cleanup_expired_messages() == 0

    moderator = UserAccount.objects.create_user(
        email="private-moderator@example.test", password="Safe-Test-Password-123!"
    )
    moderator_person = Person.objects.create(
        user=moderator, first_name="Mod", last_name="Eration"
    )
    ClassMembership.objects.create(
        person=moderator_person,
        school_class=school_class,
        valid_from=school_class.school_year.starts_on,
    )
    RoleAssignment.objects.create(
        user=moderator, school_class=school_class, role="moderator"
    )
    Authenticator.objects.create(
        user=moderator,
        type=Authenticator.Type.TOTP,
        data={"secret": "synthetic-test-only"},
    )
    client.force_login(moderator)
    assert client.get(
        f"/chat/{conversation.room.public_id}/ansicht/", secure=True
    ).status_code == 404
    assert client.post(
        f"/chat/messages/{message.public_id}/moderate/", secure=True
    ).status_code == 204
    message.refresh_from_db()
    assert message.hidden_at and message.hidden_by == moderator

    client.force_login(second)
    hidden_view = client.get(
        f"/chat/{conversation.room.public_id}/ansicht/", secure=True
    ).content.decode()
    assert "Diese Nachricht wurde von der Moderation ausgeblendet." in hidden_view
    assert "Gemeldeter Inhalt" not in hidden_view

    message.reports.update(resolved_at=timezone.now())
    assert cleanup_expired_messages() == 1
    assert not ChatMessage.objects.filter(pk=message.pk).exists()
