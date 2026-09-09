from django.db import transaction

from klasse5e.core.models import AuditEvent, Person, RelationshipStatus
from klasse5e.core.policies import visible_student_people
from klasse5e.portal_adapters.models import ChildModuleConnection, PortalAdapter
from klasse5e.portal_adapters.policies import provider_available_for_student, set_connection_state

from .crypto import encrypt
from .models import FeatureKey, WebUntisConnection, WebUntisFeaturePreference


def eligible_students(user):
    if not hasattr(user, "person"):
        return Person.objects.none()
    return Person.objects.filter(
        student_relationships__guardian_person=user.person,
        student_relationships__status=RelationshipStatus.VERIFIED,
        student_relationships__is_legal_guardian=True,
        student_relationships__may_view_student_profile=True,
    ).distinct()


def visible_connections(user):
    return WebUntisConnection.objects.filter(student__in=visible_student_people(user))


def can_manage_connection(user, student):
    return eligible_students(user).filter(pk=student.pk).exists() and provider_available_for_student(
        student, PortalAdapter.Provider.WEBUNTIS
    )


@transaction.atomic
def save_connection(*, user, student, username, password):
    if not can_manage_connection(user, student):
        raise PermissionError("WebUntis ist für dieses Kind nicht freigegeben.")
    connection, _ = WebUntisConnection.objects.update_or_create(
        user=user,
        student=student,
        defaults={
            "username_encrypted": encrypt(username),
            "password_encrypted": encrypt(password),
            "status": "not_tested",
            "status_detail": "",
            "server": "thgwob.webuntis.com",
            "school": "thgwob",
        },
    )
    for key, _label in FeatureKey.choices:
        WebUntisFeaturePreference.objects.get_or_create(connection=connection, key=key)
    AuditEvent.objects.create(
        actor=user,
        action="webuntis.credentials_saved",
        target_type="webuntis_connection",
        target_id=str(connection.pk),
        metadata={"student_id": str(student.pk)},
    )
    set_connection_state(
        student,
        PortalAdapter.Provider.WEBUNTIS,
        ChildModuleConnection.ConnectionState.CONNECTED,
    )
    return connection


def remove_connection(connection, actor):
    set_connection_state(
        connection.student,
        PortalAdapter.Provider.WEBUNTIS,
        ChildModuleConnection.ConnectionState.CREDENTIALS_NEEDED,
    )
    connection_id = connection.pk
    connection.delete()
    AuditEvent.objects.create(
        actor=actor,
        action="webuntis.connection_removed",
        target_type="webuntis_connection",
        target_id=str(connection_id),
        metadata={},
    )
