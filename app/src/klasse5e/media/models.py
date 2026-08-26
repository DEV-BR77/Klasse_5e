import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from klasse5e.core.models import Person, SchoolClass, SchoolYear, UserAccount
from klasse5e.events.models import Event


def photo_path(instance, filename):
    return f"galleries/{instance.gallery_id}/{instance.id.hex}/{filename}"


class Gallery(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Entwurf"
        PUBLISHED = "published", "Veröffentlicht"
        ARCHIVED = "archived", "Archiviert"

    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.PROTECT)
    event = models.OneToOneField(Event, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status, default=Status.DRAFT)
    upload_allowed = models.BooleanField(default=False)
    download_allowed = models.BooleanField(default=False)
    moderation_required = models.BooleanField(default=True)
    retention_until = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(UserAccount, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.event_id and (
            self.event.school_class_id != self.school_class_id
            or self.event.school_year_id != self.school_year_id
        ):
            raise ValidationError("event_class_mismatch")

    def save(self, *args, **kwargs):
        if not self.retention_until and self.school_year_id:
            from django.conf import settings

            self.retention_until = timezone.make_aware(
                timezone.datetime.combine(self.school_year.ends_on, timezone.datetime.min.time())
            ) + timezone.timedelta(days=settings.GALLERY_RETENTION_GRACE_DAYS)
        super().save(*args, **kwargs)


class Photo(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ausstehend"
        CLARIFICATION = "clarification", "Klärung"
        PUBLISHED = "published", "Veröffentlicht"
        REJECTED = "rejected", "Abgelehnt"
        HIDDEN = "hidden", "Ausgeblendet"
        WITHDRAWN = "withdrawn", "Zurückgezogen"
        DELETED = "deleted", "Gelöscht"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name="photos")
    status = models.CharField(max_length=20, choices=Status, default=Status.PENDING)
    uploader = models.ForeignKey(UserAccount, on_delete=models.PROTECT)
    original_name = models.CharField(max_length=180)
    display_file = models.FileField(upload_to=photo_path)
    thumbnail_file = models.FileField(upload_to=photo_path)
    download_file = models.FileField(upload_to=photo_path, blank=True)
    content_type = models.CharField(max_length=20)
    size = models.PositiveBigIntegerField()
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    sha256 = models.CharField(max_length=64)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderator = models.ForeignKey(
        UserAccount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moderated_photos",
    )
    reason_code = models.CharField(max_length=40, blank=True)
    retention_until = models.DateTimeField()
    description = models.CharField(max_length=500, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    download_allowed = models.BooleanField(default=False)
    biometric_analysis_allowed = models.BooleanField(
        default=False,
        help_text="Separate ausdrückliche Freigabe für die lokale technische Analyse",
    )


class PhotoSubjectDeclaration(models.Model):
    class Kind(models.TextChoices):
        NONE = "none", "Keine erkennbare Person"
        ADULTS = "adults", "Nur Erwachsene"
        KNOWN = "known", "Bekannte Person"
        UNCLEAR = "unclear", "Weitere oder unklare Person"

    class Status(models.TextChoices):
        PROPOSED = "proposed", "Vorgeschlagen"
        CONFIRMED = "confirmed", "Bestätigt"
        REJECTED = "rejected", "Abgelehnt"

    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name="subject_declarations")
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.PROTECT)
    kind = models.CharField(max_length=16, choices=Kind)
    declared_by = models.ForeignKey(
        UserAccount, on_delete=models.PROTECT, related_name="photo_declarations"
    )
    confirmed_by = models.ForeignKey(
        UserAccount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="confirmed_photo_declarations",
    )
    status = models.CharField(max_length=16, choices=Status, default=Status.PROPOSED)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)


class PhotoReport(models.Model):
    class Reason(models.TextChoices):
        CONSENT = "missing_consent", "Fehlende Zustimmung"
        PERSON = "wrong_person", "Falsche Personenangabe"
        CONTENT = "inappropriate", "Ungeeigneter Inhalt"
        PRIVACY = "privacy", "Datenschutz"
        ACCIDENTAL = "accidental", "Versehentlicher Upload"
        OTHER = "other", "Sonstiger Hinweis"

    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey(UserAccount, on_delete=models.PROTECT)
    reason = models.CharField(max_length=24, choices=Reason)
    note = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=16, default="open")
    handled_by = models.ForeignKey(
        UserAccount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="handled_photo_reports",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    handled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["photo", "reporter", "reason"], name="unique_photo_report"
            )
        ]


class PhotoModerationDecision(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name="decisions")
    moderator = models.ForeignKey(UserAccount, on_delete=models.PROTECT)
    decision = models.CharField(max_length=24)
    reason = models.CharField(max_length=40, blank=True)
    decided_at = models.DateTimeField(default=timezone.now)
    consent_policy_version = models.CharField(max_length=32, default="photo-policy-v1")
