from django.utils import timezone

from klasse5e.events.models import Event

from .models import UserNotification


def remove_event_notifications(event):
    """Remove every personal notice that leads to an event being deleted."""

    return UserNotification.objects.filter(
        school_class=event.school_class,
        object_type="event",
        object_id=str(event.pk),
    ).delete()


def purge_stale_event_notifications(*, user=None, school_class=None):
    """Remove legacy event notices whose target event no longer exists.

    Event notifications store the target id as a stable string instead of a
    foreign key so different notification producers can share one model.  This
    repair step keeps old rows from becoming dead links after an event was
    removed through an older code path or the administration.
    """

    notifications = UserNotification.objects.filter(object_type="event")
    if user is not None:
        notifications = notifications.filter(user=user)
    if school_class is not None:
        notifications = notifications.filter(school_class=school_class)

    class_ids = list(notifications.values_list("school_class_id", flat=True).distinct())
    deleted_count = 0
    for class_id in class_ids:
        event_ids = {
            str(event_id)
            for event_id in Event.objects.filter(school_class_id=class_id).values_list(
                "pk", flat=True
            )
        }
        stale_ids = [
            notification_id
            for notification_id, object_id in notifications.filter(
                school_class_id=class_id
            ).values_list("pk", "object_id")
            if object_id not in event_ids
        ]
        if stale_ids:
            deleted_count += UserNotification.objects.filter(pk__in=stale_ids).delete()[0]
    return deleted_count
