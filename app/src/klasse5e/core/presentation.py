from django.utils import timezone

from klasse5e.events.models import Event

from .models import ClassMembership, UserNotification


def is_portal_presentation_event(event):
    """Return whether an event is the deliberately featured portal introduction."""

    title = (event.title or "").casefold()
    return any(word in title for word in ("vorstell", "kennenlernen")) and any(
        word in title for word in ("portal", "klassid")
    )


def presentation_events_for_class(school_class):
    return [
        event
        for event in Event.objects.filter(
            school_class=school_class,
            status=Event.Status.PUBLISHED,
            ends_at__gte=timezone.now(),
        ).order_by("starts_at")
        if is_portal_presentation_event(event)
    ]


def ensure_presentation_notifications(user, school_class):
    """Create the neutral in-app notice lazily for every active class member."""

    if not school_class:
        return
    if not ClassMembership.objects.filter(
        school_class=school_class,
        person__user=user,
        status="active",
    ).exists():
        return
    for event in presentation_events_for_class(school_class):
        UserNotification.objects.get_or_create(
            user=user,
            school_class=school_class,
            object_type="event",
            object_id=str(event.pk),
            revision="portal-presentation-v1",
            defaults={
                "category": "news",
                "title": "Vorstellung des Klassenportals",
                "summary": f"{event.title} · {event.starts_at:%d.%m.%Y, %H:%M} Uhr",
                "target_url": f"/mehr/veranstaltungen/{event.pk}/",
            },
        )
