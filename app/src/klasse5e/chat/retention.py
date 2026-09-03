from datetime import timedelta

from django.utils import timezone

from .models import ChatMessage


def cleanup_expired_messages(*, now=None):
    now = now or timezone.now()
    deleted = 0
    for message in ChatMessage.objects.select_related("room__retention_category").iterator():
        category = message.room.retention_category
        days = category.retention_days if category else (365 if message.room.event_id else 30)
        if message.created_at >= now - timedelta(days=days):
            continue
        if message.attachment:
            message.attachment.delete(save=False)
        message.delete()
        deleted += 1
    return deleted
