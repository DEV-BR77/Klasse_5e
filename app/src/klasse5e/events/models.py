from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from klasse5e.content.models import Post, ProtectedDocument
from klasse5e.core.models import SchoolClass, SchoolYear, UserAccount


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Entwurf"
        PUBLISHED = "published", "Veröffentlicht"
        CANCELLED = "cancelled", "Abgesagt"

    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    description = models.TextField()
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    location = models.CharField(max_length=200)
    organizers = models.ManyToManyField(UserAccount, related_name="organized_events")
    change_deadline = models.DateTimeField()
    status = models.CharField(max_length=16, choices=Status, default=Status.DRAFT)
    documents = models.ManyToManyField(ProtectedDocument, blank=True)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)


class ContributionCategory(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)


class ContributionItem(models.Model):
    category = models.ForeignKey(
        ContributionCategory, on_delete=models.CASCADE, related_name="items"
    )
    label = models.CharField(max_length=160)
    desired_quantity = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    unit = models.CharField(max_length=40)
    is_free_entry = models.BooleanField(default=False)
    moderated = models.BooleanField(default=True)

    @property
    def remaining(self):
        total = self.reservations.filter(status="active").aggregate(value=models.Sum("quantity"))[
            "value"
        ] or Decimal("0")
        return max(Decimal("0"), self.desired_quantity - total)


class Reservation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Aktiv"
        CANCELLED = "cancelled", "Zurückgenommen"

    item = models.ForeignKey(
        ContributionItem, on_delete=models.CASCADE, related_name="reservations"
    )
    user = models.ForeignKey(UserAccount, on_delete=models.PROTECT)
    quantity = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    note = models.CharField(max_length=300, blank=True)
    idempotency_key = models.CharField(max_length=80)
    status = models.CharField(max_length=16, choices=Status, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "idempotency_key"], name="unique_reservation_request"
            )
        ]


class ReminderDelivery(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    reason = models.CharField(max_length=64)
    delivered_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "user", "reason"], name="unique_event_reminder"
            )
        ]
