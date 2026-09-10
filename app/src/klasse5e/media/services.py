import hashlib
import io
import re
import warnings
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone
from PIL import Image, ImageOps, UnidentifiedImageError

from klasse5e.core.models import AuditEvent

from .models import Photo, PhotoModerationDecision
from .policies import PHOTO_POLICY_VERSION, photo_consent_result


def review_due_at(now=None):
    """Return the 48-hour review target for a newly submitted photo."""
    return (now or timezone.now()) + timezone.timedelta(hours=48)


def correction_deadline(now=None):
    """Give a declined submission until the second following midnight to recover."""
    local_day = timezone.localdate(now or timezone.now())
    return timezone.make_aware(
        timezone.datetime.combine(local_day + timezone.timedelta(days=2), timezone.datetime.min.time())
    )


def safe_original_name(name):
    value = re.sub(r"[^A-Za-z0-9._-]", "_", Path(name).name)[:180]
    return value or "upload"


def process_upload(upload):
    if upload.size > settings.GALLERY_MAX_UPLOAD_BYTES:
        raise ValidationError("image_too_large")
    raw = upload.read(settings.GALLERY_MAX_UPLOAD_BYTES + 1)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            image = Image.open(io.BytesIO(raw))
            image.verify()
            image = Image.open(io.BytesIO(raw))
            image.load()
    except (
        UnidentifiedImageError,
        OSError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        raise ValidationError("invalid_image") from exc
    if image.format not in {"JPEG", "PNG"}:
        raise ValidationError("unsupported_image_format")
    if image.width * image.height > settings.GALLERY_MAX_PIXELS:
        raise ValidationError("too_many_pixels")
    image = ImageOps.exif_transpose(image)
    if image.mode not in {"RGB", "RGBA"}:
        image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
    output_format = "PNG" if image.format == "PNG" and image.mode == "RGBA" else "JPEG"
    if output_format == "JPEG" and image.mode != "RGB":
        background = Image.new("RGB", image.size, "white")
        background.paste(image, mask=image.getchannel("A"))
        image = background
    display = io.BytesIO()
    image.save(display, output_format, quality=88, optimize=True)
    thumb = ImageOps.contain(image.copy(), (480, 480))
    thumbnail = io.BytesIO()
    thumb.save(thumbnail, output_format, quality=82, optimize=True)
    content_type = "image/png" if output_format == "PNG" else "image/jpeg"
    extension = "png" if output_format == "PNG" else "jpg"
    clean = display.getvalue()
    return {
        "display": clean,
        "thumbnail": thumbnail.getvalue(),
        "content_type": content_type,
        "extension": extension,
        "width": image.width,
        "height": image.height,
        "sha256": hashlib.sha256(clean).hexdigest(),
    }


def create_photo(*, gallery, uploader, upload, description=""):
    processed = process_upload(upload)
    photo = Photo(
        gallery=gallery,
        uploader=uploader,
        original_name=safe_original_name(upload.name),
        content_type=processed["content_type"],
        size=len(processed["display"]),
        width=processed["width"],
        height=processed["height"],
        sha256=processed["sha256"],
        retention_until=min(gallery.retention_until, timezone.now() + timezone.timedelta(days=365)),
        description=description[:500],
        review_due_at=review_due_at(),
    )
    photo.display_file.save(
        f"display.{processed['extension']}", ContentFile(processed["display"]), save=False
    )
    photo.thumbnail_file.save(
        f"thumbnail.{processed['extension']}", ContentFile(processed["thumbnail"]), save=False
    )
    photo.download_file.save(
        f"download.{processed['extension']}", ContentFile(processed["display"]), save=False
    )
    photo.save()
    AuditEvent.objects.create(
        actor=uploader, action="photo.uploaded", target_type="photo", target_id=str(photo.id)
    )
    return photo


@transaction.atomic
def decide_photo(photo, moderator, decision, reason=""):
    target = {
        "publish": "published",
        "reject": "rejected",
        "clarify": "clarification",
        "hide": "hidden",
        "delete": "deleted",
    }.get(decision)
    if not target:
        raise ValidationError("invalid_decision")
    if decision == "publish":
        allowed, code = photo_consent_result(photo)
        if not allowed:
            raise ValidationError(code)
    if decision == "reject" and photo.resubmission_count == 0:
        # The first rejection is a recoverable correction request. A renewed
        # submission may happen once before the documented deadline.
        target = Photo.Status.CLARIFICATION
        photo.correction_deadline = correction_deadline()
    elif decision == "reject":
        # A second rejection is final; originals and derived files must not
        # remain in the protected media area.
        target = Photo.Status.DELETED
        photo.finalized_at = timezone.now()
    else:
        photo.correction_deadline = None
        if target in {Photo.Status.PUBLISHED, Photo.Status.HIDDEN, Photo.Status.DELETED}:
            photo.finalized_at = timezone.now()
    photo.status = target
    photo.moderator = moderator
    photo.moderated_at = timezone.now()
    photo.reason_code = reason[:40]
    photo.save(update_fields=[
        "status", "moderator", "moderated_at", "reason_code", "correction_deadline", "finalized_at"
    ])
    PhotoModerationDecision.objects.create(
        photo=photo,
        moderator=moderator,
        decision=decision,
        reason=reason[:40],
        consent_policy_version=PHOTO_POLICY_VERSION,
    )
    AuditEvent.objects.create(
        actor=moderator, action=f"photo.{decision}", target_type="photo", target_id=str(photo.id)
    )
    if decision == "delete" or (decision == "reject" and target == Photo.Status.DELETED):
        delete_photo_files(photo)


@transaction.atomic
def resubmit_photo(photo, uploader, *, upload=None, description=None):
    """Return one declined photo to the review queue, optionally replacing its file."""
    now = timezone.now()
    if photo.uploader_id != uploader.id:
        raise ValidationError("not_uploader")
    if photo.status != Photo.Status.CLARIFICATION:
        raise ValidationError("photo_not_waiting_for_correction")
    if photo.resubmission_count >= 1:
        raise ValidationError("resubmission_limit_reached")
    if not photo.correction_deadline or photo.correction_deadline <= now:
        raise ValidationError("correction_deadline_expired")
    if upload is not None:
        processed = process_upload(upload)
        for field_name in ("display_file", "thumbnail_file", "download_file"):
            field = getattr(photo, field_name)
            if field:
                field.delete(save=False)
        photo.original_name = safe_original_name(upload.name)
        photo.content_type = processed["content_type"]
        photo.size = len(processed["display"])
        photo.width = processed["width"]
        photo.height = processed["height"]
        photo.sha256 = processed["sha256"]
        photo.display_file.save(
            f"display.{processed['extension']}", ContentFile(processed["display"]), save=False
        )
        photo.thumbnail_file.save(
            f"thumbnail.{processed['extension']}", ContentFile(processed["thumbnail"]), save=False
        )
        photo.download_file.save(
            f"download.{processed['extension']}", ContentFile(processed["display"]), save=False
        )
    if description is not None:
        photo.description = description[:500]
    photo.status = Photo.Status.PENDING
    photo.resubmission_count += 1
    photo.review_due_at = review_due_at(now)
    photo.correction_deadline = None
    photo.moderator = None
    photo.moderated_at = None
    photo.reason_code = ""
    photo.save()
    PhotoModerationDecision.objects.create(
        photo=photo,
        moderator=uploader,
        decision="resubmitted",
        consent_policy_version=PHOTO_POLICY_VERSION,
    )
    AuditEvent.objects.create(
        actor=uploader, action="photo.resubmitted", target_type="photo", target_id=str(photo.id)
    )
    return photo


def delete_photo_files(photo):
    for field_name in ("display_file", "thumbnail_file", "download_file"):
        field = getattr(photo, field_name)
        if field:
            field.delete(save=False)
    photo.subject_declarations.all().delete()
    photo.decisions.all().delete()
    photo.reports.all().delete()
    photo.status = Photo.Status.DELETED
    photo.deleted_at = timezone.now()
    photo.display_file = ""
    photo.thumbnail_file = ""
    photo.download_file = ""
    photo.save(
        update_fields=["status", "deleted_at", "display_file", "thumbnail_file", "download_file"]
    )
