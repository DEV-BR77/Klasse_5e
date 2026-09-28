"""Saved role grants must change real domain access, including direct requests."""

from datetime import date

import pytest
from allauth.mfa.models import Authenticator
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from klasse5e.chat.models import ChatMessage, ChatRoom, ChatRoomMember, DirectConversation
from klasse5e.chat.services import may_create_room, may_moderate, require_room_access
from klasse5e.core.models import (
    ClassMembership, PortalModule, PortalModuleOverride, Role, RoleAssignment, RoleModulePermission,
    School, SchoolClass, UserAccount,
)
from klasse5e.core.module_permissions import role_allows_module_action
from klasse5e.events.models import Event, EventPoll
from klasse5e.events.policies import may_create_event, may_manage_event
from klasse5e.media.models import Gallery
from klasse5e.media.policies import may_manage_gallery
from klasse5e.schedule.models import CalendarEntry
from klasse5e.schedule.services import update_calendar_entry

pytestmark = pytest.mark.django_db


def grant(role, module, action, *, active=True, scope="platform"):
    return RoleModulePermission.objects.update_or_create(
        role=role, module=PortalModule.objects.get(key=module), action=action,
        defaults={"active": active, "scope": scope},
    )[0]


@pytest.fixture
def manager(guardian, school_class):
    RoleAssignment.objects.create(user=guardian, role=Role.CONTENT_MANAGER, school_class=school_class)
    Authenticator.objects.create(
        user=guardian, type=Authenticator.Type.TOTP, data={"secret": "synthetic-test-only"},
    )
    return guardian


def room_for(school_class):
    return ChatRoom.objects.create(
        title="Rechteprüfung", school_class=school_class, school_year=school_class.school_year,
    )


def test_saved_grant_controls_chat_button_and_direct_post(client, admin_user, manager, school_class):
    module = PortalModule.objects.get(key="chat")
    client.force_login(admin_user)
    response = client.post("/verwaltung/rollen/berechtigungen/", {
        "role": Role.CONTENT_MANAGER,
        f"permission-{module.pk}-create": "off",
        f"scope-{module.pk}-create": "platform",
    }, secure=True)
    assert response.status_code == 302
    client.force_login(manager)
    response = client.get("/chat/", secure=True)
    assert response.status_code == 200
    assert b'data-dialog-open="new-chat-room"' not in response.content
    assert client.post("/chat/", {"title": "Nicht erlaubt"}, secure=True).status_code == 404
    assert not ChatRoom.objects.filter(title="Nicht erlaubt").exists()
    client.force_login(admin_user)
    response = client.post("/verwaltung/rollen/berechtigungen/", {
        "role": Role.CONTENT_MANAGER,
        f"permission-{module.pk}-create": "on",
        f"scope-{module.pk}-create": "class",
    }, secure=True)
    assert response.status_code == 302
    client.force_login(manager)
    assert b'data-dialog-open="new-chat-room"' in client.get("/chat/", secure=True).content
    assert client.post("/chat/", {"title": "Erlaubter Raum"}, secure=True).status_code == 302
    assert ChatRoom.objects.filter(title="Erlaubter Raum", school_class=school_class).exists()


@pytest.mark.parametrize("action", ["view", "read", "create"])
def test_missing_prerequisite_denies_elevated_action_but_keeps_membership(manager, school_class, action):
    grant(Role.CONTENT_MANAGER, "chat", action, active=False)
    assert not may_create_room(manager, school_class)
    require_room_access(manager, room_for(school_class))


def test_assignment_boundary_cannot_be_widened_by_platform_scope(manager, school_class, year):
    other_school = School.objects.create(name="Andere Schule", slug="other-permission")
    other_class = SchoolClass.objects.create(school=other_school, school_year=year, name="6a", code="6a")
    ClassMembership.objects.create(person=manager.person, school_class=other_class, valid_from=date(2026, 8, 1))
    assert may_create_room(manager, school_class)
    assert not may_create_room(manager, other_class)
    assignment = RoleAssignment.objects.get(user=manager, role=Role.CONTENT_MANAGER)
    assignment.school_class = None
    assignment.school = school_class.school
    assignment.save()
    assert may_create_room(manager, school_class)
    assert not may_create_room(manager, other_class)
    assignment.school = None
    assignment.save()
    assert may_create_room(manager, other_class)


@pytest.mark.parametrize("scope", ["platform", "school", "class", "own"])
def test_membership_revocation_denies_managed_role_in_every_scope(manager, school_class, scope):
    grant(Role.CONTENT_MANAGER, "chat", "create", scope=scope)
    assert may_create_room(manager, school_class)
    manager.person.classmembership_set.update(status="revoked")
    assert not may_create_room(manager, school_class)


def test_own_scope_requires_explicit_ownership_and_no_stale_permission_cache(manager, school_class):
    grant(Role.CONTENT_MANAGER, "events", "edit", scope="own")
    assert role_allows_module_action(manager, "events", "edit", school_class, owner_id=manager.pk)
    assert not role_allows_module_action(manager, "events", "edit", school_class)
    assert not role_allows_module_action(manager, "events", "edit", school_class, owner_id=manager.pk + 1)
    grant(Role.CONTENT_MANAGER, "events", "edit", active=False)
    assert not role_allows_module_action(manager, "events", "edit", school_class, owner_id=manager.pk)


def test_locked_user_and_disabled_module_cannot_use_grant(manager, school_class):
    manager.locked_at = timezone.now()
    manager.save()
    assert not may_create_room(manager, school_class)
    manager.locked_at = None
    manager.save()
    PortalModule.objects.filter(key="chat").update(default_enabled=False)
    assert not may_create_room(manager, school_class)


def test_roles_are_additive(manager, school_class):
    grant(Role.CONTENT_MANAGER, "chat", "create", active=False)
    RoleAssignment.objects.create(user=manager, role=Role.EDITOR, school_class=school_class)
    grant(Role.EDITOR, "chat", "create")
    assert may_create_room(manager, school_class)
    RoleAssignment.objects.filter(user=manager, role=Role.EDITOR).update(active=False)
    assert not may_create_room(manager, school_class)


def test_moderation_revocation_controls_real_endpoint(client, manager, school_class):
    room = room_for(school_class)
    message = ChatMessage.objects.create(room=room, author=manager, body="Prüfnachricht")
    grant(Role.CONTENT_MANAGER, "chat", "moderate", active=False)
    client.force_login(manager)
    url = f"/chat/messages/{message.public_id}/moderate/"
    assert client.post(url, secure=True).status_code == 404
    grant(Role.CONTENT_MANAGER, "chat", "moderate")
    assert may_moderate(manager, room)
    assert client.post(url, secure=True).status_code == 204
    message.refresh_from_db()
    assert message.hidden_by_id == manager.pk


def test_role_grant_does_not_expose_private_conversation(client, admin_user, manager, school_class):
    other = UserAccount.objects.create_user("other-private@example.test", password=None)
    room = room_for(school_class)
    DirectConversation.objects.create(
        room=room, school_class=school_class, participant_one=manager, participant_two=other,
    )
    message = ChatMessage.objects.create(room=room, author=manager, body="Privat")
    with pytest.raises(PermissionDenied):
        require_room_access(admin_user, room)
    client.force_login(admin_user)
    assert client.get(f"/chat/{room.public_id}/ansicht/", secure=True).status_code == 404
    assert client.post(f"/chat/messages/{message.public_id}/moderate/", secure=True).status_code == 404


def test_primary_admin_read_revocation_does_not_lock_role_editor(client, admin_user, school_class):
    room = room_for(school_class)
    require_room_access(admin_user, room)
    grant(Role.PRIMARY_ADMIN, "chat", "read", active=False)
    with pytest.raises(PermissionDenied):
        require_room_access(admin_user, room)
    client.force_login(admin_user)
    assert client.get("/verwaltung/rollen/berechtigungen/", secure=True).status_code == 200


def test_event_publication_and_edit_rights(manager, school_class):
    assert may_create_event(manager, school_class)
    grant(Role.CONTENT_MANAGER, "events", "publish", active=False)
    assert not may_create_event(manager, school_class)
    now = timezone.now()
    event = Event.objects.create(
        school_class=school_class, school_year=school_class.school_year, title="Termin",
        starts_at=now, ends_at=now + timezone.timedelta(hours=1), change_deadline=now,
        status="published",
    )
    assert may_manage_event(manager, event)
    grant(Role.CONTENT_MANAGER, "events", "edit", active=False)
    assert not may_manage_event(manager, event)
    event.organizers.add(manager)
    assert may_manage_event(manager, event)  # independent, object-specific organizer right


def test_calendar_revocation_stops_service_write(manager, school_class):
    now = timezone.now()
    entry = CalendarEntry.objects.create(
        school_class=school_class, school_year=school_class.school_year,
        kind="exam", title="Original", starts_at=now, ends_at=now + timezone.timedelta(hours=1),
    )
    for action in ("view", "read", "edit"):
        grant(Role.CONTENT_MANAGER, "calendar", action)
    update_calendar_entry(entry, manager, title="Erlaubt")
    grant(Role.CONTENT_MANAGER, "calendar", "edit", active=False)
    with pytest.raises(PermissionDenied):
        update_calendar_entry(entry, manager, title="Verboten")
    entry.refresh_from_db()
    assert entry.title == "Erlaubt"


def test_gallery_moderation_and_publication_are_distinct(manager, school_class):
    gallery = Gallery.objects.create(
        school_class=school_class, school_year=school_class.school_year,
        created_by=manager, title="Galerie", status="published",
    )
    for action in ("view", "read", "moderate"):
        grant(Role.CONTENT_MANAGER, "gallery", action)
    assert may_manage_gallery(manager, gallery)
    assert not may_manage_gallery(manager, gallery, "publish")
    grant(Role.CONTENT_MANAGER, "gallery", "moderate", active=False)
    assert not may_manage_gallery(manager, gallery)


def test_personal_modules_expose_no_ineffective_role_controls(client, admin_user):
    module = PortalModule.objects.get(key="webuntis_timetable")
    client.force_login(admin_user)
    response = client.get("/verwaltung/rollen/berechtigungen/", secure=True)
    assert f'name="permission-{module.pk}-read"'.encode() not in response.content
    assert client.post("/verwaltung/rollen/berechtigungen/", {
        "role": Role.CONTENT_MANAGER, f"permission-{module.pk}-read": "on",
        f"scope-{module.pk}-read": "platform",
    }, secure=True).status_code == 400


def test_room_edit_cannot_bypass_archive_permission(client, manager, school_class):
    room = room_for(school_class)
    client.force_login(manager)
    payload = {"action": "save", "room_id": str(room.public_id), "title": "Umbenannt", "is_open": "on"}
    assert client.post("/chat/", payload, secure=True).status_code == 302
    payload.pop("is_open")
    assert client.post("/chat/", payload, secure=True).status_code == 404
    room.refresh_from_db()
    assert room.is_open
    grant(Role.CONTENT_MANAGER, "chat", "moderate")
    assert client.post("/chat/", payload, secure=True).status_code == 302
    room.refresh_from_db()
    assert not room.is_open


def test_expired_class_member_cannot_be_added_to_room(client, admin_user, manager, school_class):
    room = room_for(school_class)
    manager.person.classmembership_set.update(valid_until=timezone.localdate() - timezone.timedelta(days=1))
    client.force_login(admin_user)
    url = f"/chat/{room.public_id}/ansicht/"
    payload = {"action": "member_add", "user_id": str(manager.pk), "role": "moderator"}
    assert client.post(url, payload, secure=True).status_code == 302
    assert not ChatRoomMember.objects.filter(room=room, user=manager).exists()
    manager.person.classmembership_set.update(valid_until=None)
    assert client.post(url, payload, secure=True).status_code == 302
    assert ChatRoomMember.objects.filter(room=room, user=manager, active=True).exists()


@pytest.mark.parametrize("role", [Role.PRIMARY_ADMIN, Role.CONTENT_MANAGER, Role.EDITOR, Role.MODERATOR])
def test_explicit_grant_works_for_each_managed_role(manager, school_class, settings, role):
    from klasse5e.biometrics.policies import may_manage_biometrics
    from klasse5e.mobility.views import _can_moderate

    settings.BIOMETRIC_SEARCH_ENABLED = True
    PortalModuleOverride.objects.create(
        module=PortalModule.objects.get(key="photo_memory"), school_class=school_class, enabled=True,
    )
    RoleAssignment.objects.filter(user=manager).update(active=False)
    RoleAssignment.objects.create(user=manager, role=role, school=school_class.school)
    for module, check in (("photo_memory", may_manage_biometrics), ("mobility", _can_moderate)):
        for action in ("view", "read", "moderate"):
            grant(role, module, action)
        assert check(manager, school_class)
        grant(role, module, "moderate", active=False)
        assert not check(manager, school_class)


@pytest.mark.parametrize("module", ["pdf_forms", "events", "calendar"])
def test_role_read_revocation_covers_secondary_views(client, admin_user, school_class, module):
    now = timezone.now()
    event = Event.objects.create(
        school_class=school_class, school_year=school_class.school_year, title="Leserechte",
        starts_at=now, ends_at=now + timezone.timedelta(hours=1), change_deadline=now,
        status="published",
    )
    poll = EventPoll.objects.create(
        school_class=school_class, title="Terminauswahl", created_by=admin_user,
        closes_at=now + timezone.timedelta(days=1),
    )
    urls = {
        "pdf_forms": ["/mehr/dokumente/"],
        "events": [f"/events/{event.pk}/", f"/mehr/veranstaltungen/umfrage/{poll.pk}/"],
        "calendar": [f"/schedule/classes/{school_class.pk}/week/"],
    }[module]
    client.force_login(admin_user)
    for url in urls:
        assert client.get(url, secure=True).status_code == 200
    grant(Role.PRIMARY_ADMIN, module, "read", active=False)
    for url in urls:
        assert client.get(url, secure=True).status_code == 404
    if module == "events":
        assert client.post(urls[-1], {"options": []}, secure=True).status_code == 404
