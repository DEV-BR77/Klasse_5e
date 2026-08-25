from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from web_push_kit import DeliveryStatus

from klasse5e.core.models import AuditEvent, Person, PushSubscription, UserAccount
from klasse5e.events.models import (
    ContributionCategory,
    ContributionItem,
    Event,
    ReminderDelivery,
)
from klasse5e.events.services import (
    cancel_reservation_for_user,
    create_reservation,
    send_event_reminder,
)


@pytest.fixture
def event(db, guardian, school_class, year):
    value = Event.objects.create(
        school_class=school_class,
        school_year=year,
        title="Synthetisches Fest",
        description="Test",
        starts_at=timezone.now() + timedelta(days=5),
        ends_at=timezone.now() + timedelta(days=5, hours=2),
        location="Testort",
        change_deadline=timezone.now() + timedelta(days=3),
        status="published",
    )
    value.organizers.add(guardian)
    return value


@pytest.fixture
def item(event):
    category = ContributionCategory.objects.create(event=event, name="Getränke")
    return ContributionItem.objects.create(
        category=category, label="Wasser", desired_quantity=2, unit="Flaschen"
    )


@pytest.mark.django_db
def test_event_is_class_protected(client, guardian, event):
    client.force_login(guardian)
    assert client.get(f"/events/{event.id}/").status_code == 200
    outsider = UserAccount.objects.create_user("outsider2@example.test", "Pass-123456789!")
    Person.objects.create(user=outsider, first_name="Out", last_name="Synthetic")
    client.force_login(outsider)
    assert client.get(f"/events/{event.id}/").status_code == 404


@pytest.mark.django_db
def test_reservation_quantity_idempotency_and_audit(guardian, item):
    reservation, created = create_reservation(
        item_id=item.id, user=guardian, quantity="1", note="Test", idempotency_key="request-1"
    )
    repeated, second_created = create_reservation(
        item_id=item.id, user=guardian, quantity="1", note="Test", idempotency_key="request-1"
    )
    assert created and not second_created and repeated.id == reservation.id
    assert item.remaining == Decimal("1")
    assert AuditEvent.objects.filter(action="reservation.created").count() == 1


@pytest.mark.django_db
def test_no_overbooking_and_deadline(guardian, item, event):
    create_reservation(
        item_id=item.id, user=guardian, quantity="2", note="", idempotency_key="full"
    )
    with pytest.raises(ValidationError):
        create_reservation(
            item_id=item.id, user=guardian, quantity="1", note="", idempotency_key="too-much"
        )
    event.change_deadline = timezone.now() - timedelta(seconds=1)
    event.save()
    with pytest.raises(ValidationError):
        create_reservation(
            item_id=item.id, user=guardian, quantity="1", note="", idempotency_key="late"
        )


@pytest.mark.django_db
def test_free_entry_and_cancel_ownership(guardian, item):
    item.is_free_entry = True
    item.save()
    reservation, _ = create_reservation(
        item_id=item.id, user=guardian, quantity="1", note="Eigener Eintrag", idempotency_key="free"
    )
    other = UserAccount.objects.create_user("other@example.test", "Pass-123456789!")
    with pytest.raises(PermissionDenied):
        cancel_reservation_for_user(reservation, other)
    cancel_reservation_for_user(reservation, guardian)
    reservation.refresh_from_db()
    assert reservation.status == "cancelled"


class Sender:
    def __init__(self, status):
        self.status = status

    def send(self, subscription, payload):
        return SimpleNamespace(status=self.status)


@pytest.mark.django_db
def test_stale_subscription_removed_and_reminder_deduplicated(guardian, event):
    PushSubscription.from_values(guardian, "https://push.example.test/stale", "key", "auth")
    assert (
        send_event_reminder(
            event=event, user=guardian, reason="upcoming", sender=Sender(DeliveryStatus.STALE)
        )
        == "recorded"
    )
    assert not PushSubscription.objects.exists()
    assert (
        send_event_reminder(
            event=event, user=guardian, reason="upcoming", sender=Sender(DeliveryStatus.DELIVERED)
        )
        == "duplicate"
    )
    assert ReminderDelivery.objects.count() == 1


@pytest.mark.django_db
def test_temporary_push_is_retryable(guardian, event):
    PushSubscription.from_values(guardian, "https://push.example.test/temp", "key", "auth")
    assert (
        send_event_reminder(
            event=event,
            user=guardian,
            reason="change",
            sender=Sender(DeliveryStatus.TEMPORARY_FAILURE),
        )
        == "temporary_failure"
    )
    assert not ReminderDelivery.objects.exists() and PushSubscription.objects.exists()


@pytest.mark.django_db
def test_reservation_endpoint_requires_idempotency_key(client, guardian, item):
    client.force_login(guardian)
    assert client.post(f"/items/{item.id}/reserve/", {"quantity": "1"}).status_code == 400
    response = client.post(
        f"/items/{item.id}/reserve/", {"quantity": "1"}, HTTP_IDEMPOTENCY_KEY="web-1"
    )
    assert response.status_code == 201
