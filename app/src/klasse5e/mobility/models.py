import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from klasse5e.core.models import SchoolClass


class MobilityListing(models.Model):
    class Kind(models.TextChoices):
        OFFER = "offer", "Ich biete"
        REQUEST = "request", "Ich suche"

    class Transport(models.TextChoices):
        CAR = "car", "Auto"
        BICYCLE = "bicycle", "Fahrrad"
        WALK = "walk", "Zu Fuß"

    class Direction(models.TextChoices):
        TO_SCHOOL = "to_school", "Hinweg zur Schule"
        FROM_SCHOOL = "from_school", "Rückweg von der Schule"
        BOTH = "both", "Hin- und Rückweg"

    class Status(models.TextChoices):
        ACTIVE = "active", "Aktiv"
        PAUSED = "paused", "Pausiert"
        MATCHED = "matched", "Vermittelt"
        EXPIRED = "expired", "Abgelaufen"
        WITHDRAWN = "withdrawn", "Zurückgezogen"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    kind = models.CharField(max_length=12, choices=Kind)
    transport = models.CharField(max_length=16, choices=Transport)
    direction = models.CharField(max_length=16, choices=Direction)
    title = models.CharField(max_length=160)
    approximate_area = models.CharField(max_length=120, blank=True)
    weekdays = models.JSONField(default=list)
    time_from = models.TimeField()
    time_until = models.TimeField()
    seats = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(12)])
    max_detour_km = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(50)],
    )
    valid_until = models.DateField()
    notes = models.CharField(max_length=600, blank=True)
    safety_confirmed = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=Status, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["time_from", "title"]
        indexes = [models.Index(fields=["school_class", "status", "valid_until"])]


class MeetingPoint(models.Model):
    listing = models.ForeignKey(
        MobilityListing, on_delete=models.CASCADE, related_name="meeting_points"
    )
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=240, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    meeting_time = models.TimeField(null=True, blank=True)
    position = models.PositiveSmallIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["position", "id"]


class MobilityReaction(models.Model):
    class Kind(models.TextChoices):
        INTERESTED = "interested", "Interessiert"
        SEAT_OFFERED = "seat_offered", "Platz angeboten"
        QUESTION = "question", "Rückfrage"

    class Status(models.TextChoices):
        OPEN = "open", "Offen"
        ACCEPTED = "accepted", "Angenommen"
        DECLINED = "declined", "Abgelehnt"
        WITHDRAWN = "withdrawn", "Zurückgezogen"

    listing = models.ForeignKey(MobilityListing, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    kind = models.CharField(max_length=16, choices=Kind)
    message = models.CharField(max_length=400, blank=True)
    status = models.CharField(max_length=16, choices=Status, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["listing", "user"], name="unique_mobility_reaction")
        ]


class PickupDisclosure(models.Model):
    listing = models.ForeignKey(
        MobilityListing, on_delete=models.CASCADE, related_name="pickup_disclosures"
    )
    reaction = models.OneToOneField(MobilityReaction, on_delete=models.CASCADE)
    shared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="shared_pickups"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="received_pickups"
    )
    encrypted_address = models.TextField()
    purpose = models.CharField(max_length=160, default="Vereinbarte Abholung")
    valid_until = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def address(self):
        from .crypto import decrypt_address

        return decrypt_address(self.encrypted_address)

    def set_address(self, value):
        from .crypto import encrypt_address

        self.encrypted_address = encrypt_address(value[:240])


class MobilityReport(models.Model):
    listing = models.ForeignKey(MobilityListing, on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    reason = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["listing", "reporter"], name="unique_mobility_report")
        ]


class MobilityListingView(models.Model):
    listing = models.ForeignKey(
        MobilityListing, on_delete=models.CASCADE, related_name="view_events"
    )
    viewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    viewed_on = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["listing", "viewer", "viewed_on"], name="unique_daily_mobility_view"
            )
        ]
