from web_push_kit import DeliveryStatus, NotificationPayload, Subscription

from klasse5e.core.models import PushPreference, PushSubscription, UserNotification
from klasse5e.webuntis.notifications import configured_sender

from .models import ChatMessage


def notify_mentions(message_id, *, sender=None):
    message = ChatMessage.objects.select_related("room", "author__person").get(pk=message_id)
    target_url = f"/chat/{message.room.public_id}/ansicht/"
    recipients = list(message.mentions.all())
    for user in recipients:
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
        user__in=recipients, key="push_chat_mentions", enabled=True
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
