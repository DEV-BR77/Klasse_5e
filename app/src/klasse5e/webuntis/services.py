from django.db import transaction

from klasse5e.core.models import AuditEvent, Person, RelationshipStatus

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


def can_manage_connection(user, student):
    return eligible_students(user).filter(pk=student.pk).exists()


@transaction.atomic
def save_connection(*, user, student, username, password):
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
    return connection


def remove_connection(connection, actor):
    connection_id = connection.pk
    connection.delete()
    AuditEvent.objects.create(
        actor=actor,
        action="webuntis.connection_removed",
        target_type="webuntis_connection",
        target_id=str(connection_id),
        metadata={},
    )
