from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from web_push_kit import DeliveryStatus, NotificationPayload, Subscription

from klasse5e.core.models import AuditEvent, PushSubscription
from klasse5e.core.policies import has_active_membership

from .models import ContributionItem, ReminderDelivery, Reservation


@transaction.atomic
def create_reservation(*, item_id, user, quantity, note, idempotency_key):
    existing = Reservation.objects.filter(user=user, idempotency_key=idempotency_key).first()
    if existing:
        return existing, False
    item = (
        ContributionItem.objects.select_for_update()
        .select_related("category__event__school_class")
        .get(id=item_id)
    )
    event = item.category.event
    if not has_active_membership(user, event.school_class):
        raise PermissionDenied
    if timezone.now() > event.change_deadline:
        raise ValidationError("deadline_passed")
    amount = Decimal(str(quantity))
    if amount <= 0 or amount > item.remaining:
        raise ValidationError("quantity_unavailable")
    try:
        reservation = Reservation.objects.create(
            item=item, user=user, quantity=amount, note=note[:300], idempotency_key=idempotency_key
        )
    except IntegrityError:
        return Reservation.objects.get(user=user, idempotency_key=idempotency_key), False
    AuditEvent.objects.create(
        actor=user,
        action="reservation.created",
        target_type="reservation",
        target_id=str(reservation.id),
        metadata={"item_id": item.id},
    )
    return reservation, True


@transaction.atomic
def cancel_reservation_for_user(reservation, user):
    locked = (
        Reservation.objects.select_for_update()
        .select_related("item__category__event")
        .get(id=reservation.id)
    )
    if locked.user_id != user.id:
        raise PermissionDenied
    if timezone.now() > locked.item.category.event.change_deadline:
        raise ValidationError("deadline_passed")
    if locked.status != Reservation.Status.CANCELLED:
        locked.status = Reservation.Status.CANCELLED
        locked.save(update_fields=["status"])
        AuditEvent.objects.create(
            actor=user,
            action="reservation.cancelled",
            target_type="reservation",
            target_id=str(locked.id),
        )


def send_event_reminder(*, event, user, reason, sender):
    if ReminderDelivery.objects.filter(event=event, user=user, reason=reason).exists():
        return "duplicate"
    for stored in PushSubscription.objects.filter(user=user, enabled=True):
        result = sender.send(
            Subscription(endpoint=stored.endpoint, p256dh=stored.p256dh, auth=stored.auth),
            NotificationPayload(
                title="Klasse 5e",
                body="Es gibt einen neuen Hinweis.",
                url=f"/events/{event.id}/",
                category="event",
                message_id=f"event-{event.id}-{reason}",
            ),
        )
        if result.status == DeliveryStatus.STALE:
            stored.delete()
        elif result.status == DeliveryStatus.TEMPORARY_FAILURE:
            return "temporary_failure"
    ReminderDelivery.objects.create(event=event, user=user, reason=reason)
    return "recorded"
