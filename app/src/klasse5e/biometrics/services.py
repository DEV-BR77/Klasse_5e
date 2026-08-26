import uuid

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from klasse5e.core.models import AuditEvent
from klasse5e.media.policies import may_view_photo

from .client import VisionClient
from .models import (
    BiometricCollection,
    BiometricMatch,
    BiometricProfile,
    BiometricReference,
    VisionPhotoSubmission,
)
from .policies import (
    biometric_consent,
    biometric_consent_version,
    feature_enabled,
    may_manage_biometrics,
)


def _require_feature():
    if not feature_enabled():
        raise PermissionError("biometric_feature_disabled")


@transaction.atomic
def enable_profile(student, school_class, *, actor, client=None):
    _require_feature()
    if not may_manage_biometrics(actor, school_class):
        raise PermissionError("not_allowed")
    today = timezone.localdate()
    if (
        not student.person.classmembership_set.filter(
            school_class=school_class,
            status="active",
            valid_from__lte=today,
            school_class__school_year__starts_on__lte=today,
            school_class__school_year__ends_on__gte=today,
        )
        .filter(Q(valid_until__isnull=True) | Q(valid_until__gte=today))
        .exists()
    ):
        raise PermissionError("student_outside_class")
    allowed, reason = biometric_consent(student.person)
    if not allowed:
        raise PermissionError(reason)
    collection, _ = BiometricCollection.objects.get_or_create(
        school_class=school_class,
        defaults={"pipeline_id": settings.BIOMETRIC_PIPELINE_ID},
    )
    vision = client or VisionClient()
    info = vision.create_collection(str(collection.vision_collection_id), collection.pipeline_id)
    collection.model_version = info.get("model_version", "")
    collection.save(update_fields=["model_version"])
    profile, created = BiometricProfile.objects.get_or_create(
        student=student,
        collection=collection,
        defaults={"consent_version": biometric_consent_version(student.person)},
    )
    if profile.collection_id != collection.id:
        raise PermissionError("collection_mismatch")
    if profile.status != "active":
        profile.status = "active"
        profile.deleted_at = None
        profile.deletion_requested_at = None
        profile.consent_version = biometric_consent_version(student.person)
        profile.save(
            update_fields=[
                "status",
                "deleted_at",
                "deletion_requested_at",
                "consent_version",
            ]
        )
    vision.create_subject(str(collection.vision_collection_id), str(profile.vision_subject_id))
    AuditEvent.objects.create(
        actor=actor,
        action="biometric.profile_enabled",
        target_type="biometric_profile",
        target_id=str(profile.public_id),
        metadata={"pipeline_id": collection.pipeline_id},
    )
    return profile


@transaction.atomic
def submit_photo(photo, *, actor, client=None, manual_review=False):
    _require_feature()
    gallery = photo.gallery
    if not may_manage_biometrics(actor, gallery.school_class):
        raise PermissionError("not_allowed")
    if not photo.biometric_analysis_allowed or not may_view_photo(actor, photo):
        raise PermissionError("photo_not_approved")
    collection = BiometricCollection.objects.get(school_class=gallery.school_class, status="active")
    submission, created = VisionPhotoSubmission.objects.get_or_create(
        photo=photo,
        defaults={
            "collection": collection,
            "pipeline_id": collection.pipeline_id,
            "model_version": collection.model_version,
            "source_delete_due_at": timezone.now()
            + timezone.timedelta(days=7 if manual_review else 0, hours=0 if manual_review else 24),
            "manual_review": manual_review,
        },
    )
    if not created:
        return submission
    vision = client or VisionClient()
    with photo.display_file.open("rb") as source:
        vision.upload_image(
            str(collection.vision_collection_id),
            str(submission.vision_image_id),
            source.read(),
            photo.content_type,
        )
    job = vision.analyze(
        str(collection.vision_collection_id),
        str(submission.vision_image_id),
        f"analyze-{submission.public_id}",
    )
    submission.vision_job_id = job["job_id"]
    submission.status = "ready" if job["status"] == "completed" else "analyzing"
    submission.model_version = job.get("model_version", collection.model_version)
    submission.save(update_fields=["vision_job_id", "status", "model_version"])
    if submission.status == "ready":
        import_suggestions(submission, client=vision)
    return submission


@transaction.atomic
def import_suggestions(submission, *, client=None):
    vision = client or VisionClient()
    collection_id = str(submission.collection.vision_collection_id)
    profiles = {}
    for item in BiometricProfile.objects.filter(
        collection=submission.collection, status="active"
    ).select_related("student__person"):
        allowed, _ = biometric_consent(item.student.person)
        if allowed:
            profiles[str(item.vision_subject_id)] = item
    created = []
    for face in vision.list_faces(collection_id, str(submission.vision_image_id)):
        for candidate in vision.list_matches(collection_id, face["face_id"]):
            profile = profiles.get(candidate["subject_id"])
            if profile is None:
                continue
            item, _ = BiometricMatch.objects.get_or_create(
                collection=submission.collection,
                vision_match_id=candidate["match_id"],
                defaults={
                    "submission": submission,
                    "profile": profile,
                    "vision_face_id": candidate["face_id"],
                    "score": candidate["score"],
                    "rank": candidate["rank"],
                    "pipeline_id": submission.pipeline_id,
                    "model_version": submission.model_version,
                },
            )
            created.append(item)
    return created


@transaction.atomic
def decide_match(match, *, actor, decision, add_as_reference=False, client=None):
    if not may_manage_biometrics(actor, match.collection.school_class):
        raise PermissionError("not_allowed")
    if match.status != "proposed":
        if match.status == decision and match.decided_by_id == actor.id:
            return match
        raise ValueError("decision_conflict")
    if add_as_reference:
        allowed, reason = biometric_consent(
            match.profile.student.person, "confirmed-match-reference"
        )
        if not allowed:
            raise PermissionError(reason)
    actor_id = uuid.uuid4()
    vision = client or VisionClient()
    if decision == "confirmed":
        vision.confirm(
            str(match.collection.vision_collection_id),
            match.vision_match_id,
            str(actor_id),
            add_as_reference,
        )
    elif decision == "rejected":
        vision.reject(
            str(match.collection.vision_collection_id), match.vision_match_id, str(actor_id)
        )
    else:
        raise ValueError("invalid_decision")
    match.status, match.decided_by, match.vision_actor_id = decision, actor, actor_id
    match.decided_at, match.add_as_reference = timezone.now(), add_as_reference
    match.save(
        update_fields=["status", "decided_by", "vision_actor_id", "decided_at", "add_as_reference"]
    )
    if add_as_reference:
        BiometricReference.objects.get_or_create(
            collection=match.collection,
            vision_reference_id=f"confirmed-{match.vision_match_id}",
            defaults={
                "profile": match.profile,
                "submission": match.submission,
                "vision_face_id": match.vision_face_id,
                "pipeline_id": match.pipeline_id,
                "model_version": match.model_version,
                "created_by": actor,
            },
        )
    AuditEvent.objects.create(
        actor=actor,
        action=f"biometric.match_{decision}",
        target_type="biometric_match",
        target_id=str(match.public_id),
        metadata={
            "pipeline_id": match.pipeline_id,
            "model_version": match.model_version,
            "reference_added": add_as_reference,
        },
    )
    return match


@transaction.atomic
def create_start_reference(profile, submission, face_id, *, actor, client=None):
    if profile.collection_id != submission.collection_id:
        raise PermissionError("collection_mismatch")
    if not may_manage_biometrics(actor, profile.collection.school_class):
        raise PermissionError("not_allowed")
    allowed, reason = biometric_consent(profile.student.person, "confirmed-match-reference")
    if not allowed:
        raise PermissionError(reason)
    reference = BiometricReference.objects.create(
        collection=profile.collection,
        profile=profile,
        submission=submission,
        vision_face_id=face_id,
        pipeline_id=submission.pipeline_id,
        model_version=submission.model_version,
        created_by=actor,
    )
    (client or VisionClient()).create_reference(
        str(profile.collection.vision_collection_id),
        str(profile.vision_subject_id),
        str(reference.vision_reference_id),
        face_id,
    )
    return reference


@transaction.atomic
def revoke_reference(reference, *, actor, client=None):
    if not may_manage_biometrics(actor, reference.collection.school_class):
        raise PermissionError("not_allowed")
    (client or VisionClient()).delete_reference(
        str(reference.collection.vision_collection_id),
        str(reference.profile.vision_subject_id),
        str(reference.vision_reference_id),
    )
    reference.revoked_at = timezone.now()
    reference.save(update_fields=["revoked_at"])
    return reference


def withdraw_profile(profile, *, actor=None, client=None):
    profile.status = "deletion_pending"
    profile.deletion_requested_at = timezone.now()
    profile.save(update_fields=["status", "deletion_requested_at"])
    old_subject_id = profile.vision_subject_id
    (client or VisionClient()).delete_subject(
        str(profile.collection.vision_collection_id), str(old_subject_id)
    )
    with transaction.atomic():
        BiometricMatch.objects.filter(profile=profile).delete()
        profile.status, profile.deleted_at = "deleted", timezone.now()
        profile.vision_subject_id = uuid.uuid4()
        profile.save(update_fields=["status", "deleted_at", "vision_subject_id"])
        AuditEvent.objects.create(
            actor=actor,
            action="biometric.profile_deleted",
            target_type="biometric_profile",
            target_id=str(profile.public_id),
            metadata={},
        )
    return profile
