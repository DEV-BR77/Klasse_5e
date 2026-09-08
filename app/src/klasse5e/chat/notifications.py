from django.db.models import Q
from web_push_kit import DeliveryStatus, NotificationPayload, Subscription

from klasse5e.core.models import (
    PushPreference,
    PushSubscription,
    UserNotification,
)
from klasse5e.webuntis.notifications import configured_sender

from .models import ChatMessage


def notify_mentions(message_id, *, sender=None):
    message = ChatMessage.objects.select_related("room", "author__person").get(pk=message_id)
    target_url = f"/chat/{message.room.public_id}/ansicht/"
    recipients = list(message.mentions.all())
    for user in recipients:
        if PushPreference.objects.filter(user=user, key="inapp_chat", enabled=False).exists():
            continue
        UserNotification.objects.get_or_create(
            user=user,
            school_class=message.room.school_class,
            object_type="chat_mention",
            object_id=str(message.public_id),
            revision="created",
            defaults={
                "category": "chat_mention",
                "title": "Du wurdest in einem Chat erwähnt",
                "summary": f"In „{message.room.title}“ wartet eine Erwähnung auf dich.",
                "target_url": target_url,
            },
        )
    sender = sender or configured_sender()
    if sender is None:
        return len(recipients)
    enabled = PushPreference.objects.filter(
        user__in=recipients, enabled=True
    ).filter(
        Q(key="push_chat") | Q(key="push_chat_mentions")
    ).values_list("user_id", flat=True)
    for stored in PushSubscription.objects.filter(user_id__in=enabled, enabled=True):
        result = sender.send(
            Subscription(endpoint=stored.endpoint, p256dh=stored.p256dh, auth=stored.auth),
            NotificationPayload(
                title="KlassID",
                body="Du hast eine neue persönliche Erwähnung.",
                url=target_url,
                category="chat_mention",
                message_id=f"mention-{message.public_id}",
            ),
        )
        if result.status == DeliveryStatus.STALE:
            stored.delete()
    return len(recipients)


def notify_parent_representatives(message_id):
    message = ChatMessage.objects.select_related("room").get(pk=message_id)
    from klasse5e.core.role_management import parent_representatives

    if not (message.room.parent_representative_chat or
            message.room.audience == message.room.Audience.PARENT_REPRESENTATIVES):
        return
    from .services import require_room_access
    from django.core.exceptions import PermissionDenied

    for user in parent_representatives(message.room.school_class):
        try:
            require_room_access(user, message.room)
        except PermissionDenied:
            continue
        if user.pk == message.author_id:
            continue
        UserNotification.objects.get_or_create(
            user=user, school_class=message.room.school_class,
            object_type="parent_representative_chat",
            object_id=str(message.public_id), revision="created",
            defaults={
                "category": "chat",
                "title": "Neue Nachricht im Elternvertretungs-Chat",
                "summary": f"In „{message.room.title}“ gibt es eine neue Nachricht.",
                "target_url": f"/chat/{message.room.public_id}/ansicht/",
            },
        )
