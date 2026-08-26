import uuid

from django.db import models

from klasse5e.core.models import SchoolClass, StudentProfile, UserAccount
from klasse5e.media.models import Photo


class BiometricCollection(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Aktiv"
        DISABLED = "disabled", "Deaktiviert"
        DELETION_PENDING = "deletion_pending", "Löschung ausstehend"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    school_class = models.OneToOneField(SchoolClass, on_delete=models.CASCADE)
    vision_collection_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    pipeline_id = models.CharField(max_length=80)
    model_version = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=24, choices=Status, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    disabled_at = models.DateTimeField(null=True, blank=True)


class BiometricProfile(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Aktiv"
        DELETION_PENDING = "deletion_pending", "Löschung ausstehend"
        DELETED = "deleted", "Gelöscht"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    collection = models.ForeignKey(BiometricCollection, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    vision_subject_id = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=24, choices=Status, default=Status.ACTIVE)
    consent_version = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    deletion_requested_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["collection", "student"], name="unique_biometric_student_collection"
            ),
            models.UniqueConstraint(
                fields=["collection", "vision_subject_id"], name="unique_vision_subject_collection"
            ),
        ]


class VisionPhotoSubmission(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Vorgemerkt"
        ANALYZING = "analyzing", "Analyse"
        READY = "ready", "Bereit"
        FAILED = "failed", "Fehlgeschlagen"
        SOURCE_PURGED = "source_purged", "Quelldatei entfernt"
        DELETION_PENDING = "deletion_pending", "Löschung ausstehend"
        DELETED = "deleted", "Gelöscht"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    collection = models.ForeignKey(BiometricCollection, on_delete=models.CASCADE)
    photo = models.OneToOneField(Photo, on_delete=models.CASCADE)
    vision_image_id = models.UUIDField(default=uuid.uuid4, editable=False)
    vision_job_id = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=24, choices=Status, default=Status.QUEUED)
    pipeline_id = models.CharField(max_length=80)
    model_version = models.CharField(max_length=120, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    source_delete_due_at = models.DateTimeField()
    source_deleted_at = models.DateTimeField(null=True, blank=True)
    error_code = models.CharField(max_length=64, blank=True)
    manual_review = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["collection", "vision_image_id"], name="unique_vision_image_collection"
            )
        ]


class BiometricMatch(models.Model):
    class Status(models.TextChoices):
        PROPOSED = "proposed", "Vorschlag"
        CONFIRMED = "confirmed", "Bestätigt"
        REJECTED = "rejected", "Verworfen"
        DELETED = "deleted", "Gelöscht"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    collection = models.ForeignKey(BiometricCollection, on_delete=models.CASCADE)
    submission = models.ForeignKey(VisionPhotoSubmission, on_delete=models.CASCADE)
    profile = models.ForeignKey(BiometricProfile, on_delete=models.CASCADE)
    vision_face_id = models.CharField(max_length=128)
    vision_match_id = models.CharField(max_length=128)
    score = models.FloatField(help_text="Modellwert, keine Prozentwahrscheinlichkeit")
    rank = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=16, choices=Status, default=Status.PROPOSED)
    decided_by = models.ForeignKey(UserAccount, null=True, on_delete=models.SET_NULL)
    vision_actor_id = models.UUIDField(null=True, editable=False)
    decided_at = models.DateTimeField(null=True, blank=True)
    add_as_reference = models.BooleanField(default=False)
    pipeline_id = models.CharField(max_length=80)
    model_version = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["collection", "vision_match_id"], name="unique_vision_match_collection"
            )
        ]


class BiometricReference(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    collection = models.ForeignKey(BiometricCollection, on_delete=models.CASCADE)
    profile = models.ForeignKey(BiometricProfile, on_delete=models.CASCADE)
    submission = models.ForeignKey(VisionPhotoSubmission, on_delete=models.CASCADE)
    vision_reference_id = models.CharField(max_length=128, default=uuid.uuid4, editable=False)
    vision_face_id = models.CharField(max_length=128)
    pipeline_id = models.CharField(max_length=80)
    model_version = models.CharField(max_length=120)
    created_by = models.ForeignKey(UserAccount, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["collection", "vision_reference_id"],
                name="unique_vision_reference_collection",
            )
        ]
