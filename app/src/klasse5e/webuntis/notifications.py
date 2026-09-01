from django.conf import settings
from django.db import transaction
from django.utils import timezone
from web_push_kit import (
    DeliveryStatus,
    NotificationPayload,
    Subscription,
    VapidConfig,
    WebPushSender,
)

from klasse5e.core.models import PushPreference, PushSubscription, Role, RoleAssignment


def configured_sender():
    if not settings.VAPID_PUBLIC_KEY or not settings.VAPID_PRIVATE_KEY:
        return None
    return WebPushSender(
        VapidConfig(
            public_key=settings.VAPID_PUBLIC_KEY,
            private_key=settings.VAPID_PRIVATE_KEY,
            subject=settings.VAPID_SUBJECT,
        )
    )


@transaction.atomic
def notify_terminal_sync_failure(run, *, sender=None):
    run = type(run).objects.select_for_update().get(pk=run.pk)
    if run.status != run.Status.FAILED or run.attempt_count < 3 or run.terminal_notification_sent_at:
        return False
    sender = sender or configured_sender()
    if sender is None:
        return False
    admin_ids = RoleAssignment.objects.filter(
        active=True, role__in=[Role.PRIMARY_ADMIN, Role.SCHOOL_ADMIN]
    ).values_list("user_id", flat=True)
    enabled_ids = PushPreference.objects.filter(
        user_id__in=admin_ids, key="sync_errors", enabled=True
    ).values_list("user_id", flat=True)
    for stored in PushSubscription.objects.filter(user_id__in=enabled_ids, enabled=True):
        result = sender.send(
            Subscription(endpoint=stored.endpoint, p256dh=stored.p256dh, auth=stored.auth),
            NotificationPayload(
                title="KlassID",
                body="Eine Synchronisation benötigt administrative Prüfung.",
                url="/settings/synchronisation/",
                category="sync_errors",
                message_id=f"sync-{run.pk}-terminal",
            ),
        )
        if result.status == DeliveryStatus.STALE:
            stored.delete()
    run.terminal_notification_sent_at = timezone.now()
    run.save(update_fields=["terminal_notification_sent_at"])
    return True
