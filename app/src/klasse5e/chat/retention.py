from datetime import timedelta

from django.utils import timezone

from .models import ChatMessage


def cleanup_expired_messages(*, now=None):
    now = now or timezone.now()
    deleted = 0
    for message in ChatMessage.objects.select_related("room__retention_category").iterator():
        category = message.room.retention_category
        if not category or not category.is_active or not category.automatic_deletion_enabled:
            continue
        days = category.retention_days
        if message.created_at >= now - timedelta(days=days):
            continue
        if message.reports.filter(resolved_at__isnull=True).exists():
            continue
        if message.attachment:
            message.attachment.delete(save=False)
        message.delete()
        deleted += 1
    return deleted
