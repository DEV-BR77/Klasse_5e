import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from klasse5e.chat.models import ChatRoom
from klasse5e.chat.notifications import notify_parent_representatives
from klasse5e.chat.services import create_message
from klasse5e.core.models import AuditEvent, Role, RoleAssignment, UserNotification
from klasse5e.core.role_management import set_user_role

pytestmark = pytest.mark.django_db


def test_admin_grant_revoke_and_regrant(admin_user, guardian, school_class):
    for active in [True, False, True]:
        set_user_role(admin_user, guardian, Role.PARENT_REPRESENTATIVE,
                      school_class=school_class, active=active)
        assert RoleAssignment.objects.get(user=guardian, role=Role.PARENT_REPRESENTATIVE).active == active
    set_user_role(admin_user, guardian, Role.PRIMARY_ADMIN)
    set_user_role(admin_user, guardian, Role.PRIMARY_ADMIN, active=False)
    assert not RoleAssignment.objects.get(user=guardian, role=Role.PRIMARY_ADMIN).active
    assert AuditEvent.objects.filter(action="role.revoked").count() == 2
    with pytest.raises(ValidationError):
        set_user_role(admin_user, admin_user, Role.PRIMARY_ADMIN, active=False)


@pytest.mark.parametrize("role", [Role.GUARDIAN, Role.CLASS_ADMIN, Role.SCHOOL_ADMIN])
def test_delegated_roles_cannot_escalate(guardian, admin_user, school_class, role):
    RoleAssignment.objects.filter(user=guardian).update(role=role)
    with pytest.raises(PermissionDenied):
        set_user_role(guardian, admin_user, Role.PRIMARY_ADMIN)


def test_membership_and_role_validation(admin_user, guardian, school_class):
    with pytest.raises(ValidationError):
        set_user_role(admin_user, guardian, Role.PRIMARY_ADMIN, school_class=school_class)
    with pytest.raises(ValidationError):
        set_user_role(admin_user, guardian, Role.TEACHER)
    guardian.person.classmembership_set.update(status="revoked")
    with pytest.raises(ValidationError):
        set_user_role(admin_user, guardian, Role.PARENT_REPRESENTATIVE, school_class=school_class)


def test_management_ui_and_mfa(client, guardian, admin_user, school_class):
    client.force_login(guardian)
    assert client.get("/verwaltung/rollen/", secure=True).status_code == 403
    assert client.post("/verwaltung/rollen/", {"form": "role"}, secure=True).status_code == 403
    client.force_login(admin_user)
    response = client.get("/verwaltung/rollen/", secure=True)
    assert response.status_code == 200
    assert guardian.email.encode() in response.content
    response = client.post("/verwaltung/rollen/", {
        "form": "role", "user": guardian.pk, "role": Role.PRIMARY_ADMIN, "action": "grant",
    }, secure=True)
    assert response.status_code == 302
    client.force_login(guardian)
    response = client.get("/verwaltung/rollen/", secure=True)
    assert response.status_code == 302
    assert "totp" in response.url


def test_room_selection_and_invalid_input(client, admin_user, school_class, year):
    rooms = [ChatRoom.objects.create(school_class=school_class, school_year=year, title=str(i)) for i in range(2)]
    client.force_login(admin_user)
    for room in rooms:
        assert client.post("/verwaltung/rollen/", {
            "form": "room", "room": room.pk, "enabled": "on",
        }, secure=True).status_code == 302
    assert list(ChatRoom.objects.filter(parent_representative_chat=True)) == [rooms[1]]
    assert client.post("/verwaltung/rollen/", {
        "form": "room", "room": "invalid",
    }, secure=True).status_code == 200


def test_role_form_requires_csrf(admin_user):
    from django.test import Client

    client = Client(enforce_csrf_checks=True)
    client.force_login(admin_user)
    assert client.post("/verwaltung/rollen/", {"form": "role"}, secure=True).status_code == 403


def test_only_one_representative_room_per_class(school_class, year):
    from django.db import IntegrityError

    ChatRoom.objects.create(school_class=school_class, school_year=year, title="Eins", parent_representative_chat=True)
    with pytest.raises(IntegrityError), transaction.atomic():
        ChatRoom.objects.create(school_class=school_class, school_year=year, title="Zwei", parent_representative_chat=True)


def test_notifications_transaction_membership_revocation(admin_user, guardian, school_class, year):
    from klasse5e.core.models import ClassMembership

    ClassMembership.objects.create(person=admin_user.person, school_class=school_class, valid_from=year.starts_on)
    set_user_role(admin_user, guardian, Role.PARENT_REPRESENTATIVE, school_class=school_class)
    room = ChatRoom.objects.create(school_class=school_class, school_year=year, title="Elternvertretung")
    create_message(room, admin_user, "Normaler Raum")
    assert not UserNotification.objects.exists()
    room.parent_representative_chat = True
    room.save()
    message = create_message(room, admin_user, "Vertraulicher Nachrichtentext")
    notify_parent_representatives(message)
    assert UserNotification.objects.count() == 1

    notification = UserNotification.objects.get(user=guardian)
    assert "Vertraulicher" not in notification.summary
    create_message(room, guardian, "Eigener Beitrag")
    assert UserNotification.objects.count() == 1
    with pytest.raises(RuntimeError), transaction.atomic():
        create_message(room, admin_user, "Rollback")
        raise RuntimeError
    assert UserNotification.objects.count() == 1
    set_user_role(admin_user, guardian, Role.PARENT_REPRESENTATIVE, school_class=school_class, active=False)
    create_message(room, admin_user, "Nach Rollenentzug")
    assert UserNotification.objects.count() == 1
    set_user_role(admin_user, guardian, Role.PARENT_REPRESENTATIVE, school_class=school_class)
    guardian.person.classmembership_set.update(status="revoked")
    create_message(room, admin_user, "Nach Mitgliedschaftsentzug")
    assert UserNotification.objects.count() == 1


def test_foreign_class_and_disabled_users_receive_nothing(admin_user, guardian, school_class, year):
    from klasse5e.core.models import ClassMembership, SchoolClass

    other = SchoolClass.objects.create(school=school_class.school, school_year=year, name="Andere", code="other")
    ClassMembership.objects.create(person=admin_user.person, school_class=other, valid_from=year.starts_on)
    set_user_role(admin_user, guardian, Role.PARENT_REPRESENTATIVE, school_class=school_class)
    room = ChatRoom.objects.create(school_class=other, school_year=year, title="Andere", parent_representative_chat=True)
    create_message(room, admin_user, "Andere Klasse")
    assert not UserNotification.objects.exists()
    ClassMembership.objects.create(person=admin_user.person, school_class=school_class, valid_from=year.starts_on)
    room.school_class = school_class
    room.save()
    guardian.is_active = False
    guardian.save()
    create_message(room, admin_user, "Deaktiviertes Konto")
    assert not UserNotification.objects.exists()
