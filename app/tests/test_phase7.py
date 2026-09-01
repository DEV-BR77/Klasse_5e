from datetime import date

import pytest
from allauth.mfa.models import Authenticator

from klasse5e.chat.models import ChatMessage, ChatRoom
from klasse5e.core.models import (
    ClassMembership,
    Person,
    RoleAssignment,
    School,
    SchoolClass,
    SchoolYear,
    UserAccount,
)


@pytest.fixture
def room(db):
    year = SchoolYear.objects.create(
        label="2026/27", starts_on=date(2026, 8, 1), ends_on=date(2027, 7, 31)
    )
    school = School.objects.create(name="Testschule", slug="chat-testschule")
    school_class = SchoolClass.objects.create(
        school=school, name="Test 5e", code="5e", school_year=year
    )
    return ChatRoom.objects.create(school_class=school_class, school_year=year, title="Klassenraum")


def member(room, email="member@example.test"):
    user = UserAccount.objects.create_user(email, "Test-Passwort-123!")
    person = Person.objects.create(user=user, first_name="Test", last_name="Person")
    ClassMembership.objects.create(
        person=person, school_class=room.school_class, valid_from=date(2026, 8, 1)
    )
    return user


@pytest.mark.django_db
def test_only_active_members_can_read_and_post(client, room):
    user = member(room)
    client.force_login(user)
    assert (
        client.post(f"/chat/rooms/{room.public_id}/messages/", {"body": "Hallo"}).status_code == 201
    )
    assert (
        client.get(f"/chat/rooms/{room.public_id}/messages/").json()["messages"][0]["body"]
        == "Hallo"
    )
    membership = user.person.classmembership_set.get()
    membership.status = "ended"
    membership.save()
    assert client.get(f"/chat/rooms/{room.public_id}/messages/").status_code == 404


@pytest.mark.django_db
def test_reply_must_be_same_room_and_closed_room_rejects(client, room):
    user = member(room)
    other = ChatRoom.objects.create(
        school_class=room.school_class, school_year=room.school_year, title="Event"
    )
    message = ChatMessage.objects.create(room=other, author=user, body="Andere Nachricht")
    client.force_login(user)
    assert (
        client.post(
            f"/chat/rooms/{room.public_id}/messages/",
            {"body": "Antwort", "reply_to": message.public_id},
        ).status_code
        == 404
    )
    room.is_open = False
    room.save()
    assert (
        client.post(f"/chat/rooms/{room.public_id}/messages/", {"body": "Zu spät"}).status_code
        == 404
    )


@pytest.mark.django_db
def test_author_edit_and_moderation(client, room):
    author = member(room)
    moderator = member(room, "moderator@example.test")
    RoleAssignment.objects.create(user=moderator, school_class=room.school_class, role="moderator")
    Authenticator.objects.create(
        user=moderator, type=Authenticator.Type.TOTP, data={"secret": "synthetic-test-only"}
    )
    message = ChatMessage.objects.create(room=room, author=author, body="Text")
    client.force_login(author)
    assert (
        client.patch(
            f"/chat/messages/{message.public_id}/",
            data='{"body":"Neu"}',
            content_type="application/json",
        ).status_code
        == 204
    )
    client.force_login(moderator)
    assert client.post(f"/chat/messages/{message.public_id}/moderate/").status_code == 204
    message.refresh_from_db()
    assert message.hidden_at and message.hidden_by == moderator


@pytest.mark.django_db
def test_report_is_idempotent_and_foreign_class_hidden(client, room):
    user = member(room)
    message = ChatMessage.objects.create(room=room, author=user, body="Text")
    client.force_login(user)
    url = f"/chat/messages/{message.public_id}/report/"
    assert client.post(url, {"reason": "privacy"}).status_code == 204
    assert client.post(url, {"reason": "privacy"}).status_code == 204
    assert message.reports.count() == 1
    stranger = UserAccount.objects.create_user("stranger@example.test", "Test-Passwort-123!")
    Person.objects.create(user=stranger, first_name="Fremd", last_name="Person")
    client.force_login(stranger)
    assert client.get(f"/chat/rooms/{room.public_id}/").status_code == 404
