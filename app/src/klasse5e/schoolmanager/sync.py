from django.db import transaction
from django.utils import timezone

from klasse5e.core.models import UserNotification
from klasse5e.portal_adapters.models import SchoolmanagerConnection

from .browser import PlaywrightSchoolmanagerClient
from .crypto import decrypt


@transaction.atomic
def sync_connection(connection, *, client_factory=PlaywrightSchoolmanagerClient):
    connection = SchoolmanagerConnection.objects.select_for_update().get(pk=connection.pk)
    items = client_factory(
        decrypt(connection.username_encrypted), decrypt(connection.password_encrypted)
    ).fetch()
    membership = connection.student.classmembership_set.select_related("school_class").filter(
        status="active"
    ).first()
    if membership is None:
        return 0
    created = 0
    for item in items:
        _, was_created = UserNotification.objects.get_or_create(
            user=connection.user,
            school_class=membership.school_class,
            category="schoolmanager",
            object_type=f"schoolmanager_{item.kind}",
            object_id=f"{connection.student_id}:{item.external_id}",
            revision=item.changed_at or item.title,
            defaults={
                "title": "Neue Nachricht aus dem Schulmanager" if item.kind == "messages" else "Neuer Elternbrief",
                "summary": "Zum Lesen im Schulmanager öffnen.",
                "target_url": "/mehr/benachrichtigungen/",
            },
        )
        created += int(was_created)
    connection.status = SchoolmanagerConnection.Status.OK
    connection.status_detail = f"{len(items)} Einträge gelesen"
    connection.last_checked_at = timezone.now()
    connection.last_sync_at = timezone.now()
    connection.save(update_fields=["status", "status_detail", "last_checked_at", "last_sync_at", "updated_at"])
    return created
