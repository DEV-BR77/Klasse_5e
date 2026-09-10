from urllib.parse import urlsplit

from django.conf import settings
from django.db import transaction

from klasse5e.core.models import AuditEvent, Person, RelationshipStatus
from klasse5e.core.policies import visible_student_people
from klasse5e.portal_adapters.models import ChildModuleConnection, PortalAdapter
from klasse5e.portal_adapters.policies import (
    provider_available_for_student,
    school_modules,
    set_connection_state,
)

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


def configured_integration(student):
    """Resolve the one reviewed WebUntis endpoint available to this child.

    A family never enters a host or technical school identifier. Both values
    come from the school-owned adapter and are checked against the deployment
    allowlist before credentials can be encrypted.
    """
    adapters = list(
        school_modules(student, PortalAdapter.Provider.WEBUNTIS)
        .filter(requires_child_credentials=True)
        .values_list("adapter_id", flat=True)
        .distinct()
    )
    if len(adapters) != 1:
        raise PermissionError("Für dieses Kind ist kein eindeutiger WebUntis-Zugang eingerichtet.")
    adapter = PortalAdapter.objects.get(pk=adapters[0])
    base_url = adapter.base_url
    parsed = urlsplit(base_url)
    server = (parsed.hostname or "").lower()
    if (
        parsed.scheme != "https"
        or not server
        or parsed.port is not None
        or server not in settings.WEBUNTIS_ALLOWED_HOSTS
    ):
        raise PermissionError("Der WebUntis-Server der Schule ist nicht freigegeben.")
    return adapter


def configured_endpoint(student):
    """Return the reviewed endpoint snapshot for compatibility with clients."""

    adapter = configured_integration(student)
    parsed = urlsplit(adapter.base_url)
    server = (parsed.hostname or "").lower()
    return server, adapter.institution_identifier.strip() or server.split(".", maxsplit=1)[0]


@transaction.atomic
def save_connection(*, user, student, username, password):
    if not can_manage_connection(user, student):
        raise PermissionError("WebUntis ist für dieses Kind nicht freigegeben.")
    adapter = configured_integration(student)
    server, school = configured_endpoint(student)
    connection, _ = WebUntisConnection.objects.update_or_create(
        user=user,
        student=student,
        adapter=adapter,
        defaults={
            "username_encrypted": encrypt(username),
            "password_encrypted": encrypt(password),
            "status": "not_tested",
            "status_detail": "",
            "server": server,
            "school": school,
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
        adapter=adapter,
    )
    return connection


def remove_connection(connection, actor):
    set_connection_state(
        connection.student,
        PortalAdapter.Provider.WEBUNTIS,
        ChildModuleConnection.ConnectionState.CREDENTIALS_NEEDED,
        adapter=connection.adapter,
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
