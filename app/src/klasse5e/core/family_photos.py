import secrets

from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import AuditEvent, ConsentType, FamilyPhoto, Person
from .policies import consent_state, has_active_membership
from .registration import sanitized_profile_photo


def family_photo_people(household, school_class):
    today = timezone.localdate()
    member_ids = household.members.values_list("pk", flat=True)
    active_student = Q(
        classmembership__school_class=school_class,
        classmembership__status="active",
        classmembership__valid_from__lte=today,
    ) & (Q(classmembership__valid_until__isnull=True) | Q(classmembership__valid_until__gte=today))
    guardian = Q(
        guardian_relationships__student_person__classmembership__school_class=school_class,
        guardian_relationships__student_person__classmembership__status="active",
        guardian_relationships__student_person__classmembership__valid_from__lte=today,
        guardian_relationships__status="verified",
        guardian_relationships__verified_at__isnull=False,
        guardian_relationships__may_view_student_profile=True,
        guardian_relationships__valid_from__lte=today,
    ) & (
        Q(guardian_relationships__valid_until__isnull=True)
        | Q(guardian_relationships__valid_until__gte=today)
    )
    return Person.objects.filter(pk__in=member_ids).filter(active_student | guardian).distinct()


def may_manage_family_photo(user, household, school_class):
    return bool(
        hasattr(user, "person")
        and has_active_membership(user, school_class)
        and household.members.filter(pk=user.person.pk).exists()
        and family_photo_people(household, school_class).filter(pk=user.person.pk).exists()
    )


def family_photo_is_visible(photo):
    subjects = list(photo.subjects.all())
    allowed_ids = set(family_photo_people(photo.household, photo.school_class).values_list("pk", flat=True))
    photo_consent = ConsentType.objects.filter(key="photo_gallery").first()
    return bool(
        photo.image
        and subjects
        and photo_consent
        and {subject.pk for subject in subjects}.issubset(allowed_ids)
        and all(consent_state(photo_consent, subject) == "allowed" for subject in subjects)
    )


@transaction.atomic
def save_family_photo(*, user, household, school_class, upload, subject_ids):
    if not may_manage_family_photo(user, household, school_class):
        raise PermissionDenied
    allowed_people = family_photo_people(household, school_class)
    allowed_ids = set(allowed_people.values_list("pk", flat=True))
    selected_ids = {int(value) for value in subject_ids if str(value).isdigit()}
    if not selected_ids or not selected_ids.issubset(allowed_ids):
        raise ValidationError("Bitte wähle nur die tatsächlich abgebildeten Familienmitglieder aus.")
    photo_consent = ConsentType.objects.filter(key="photo_gallery").first()
    selected_people = list(allowed_people.filter(pk__in=selected_ids))
    if not photo_consent or any(
        consent_state(photo_consent, person) != "allowed" for person in selected_people
    ):
        raise ValidationError("Für alle abgebildeten Personen ist eine aktuelle Foto-Freigabe nötig.")
    if not upload:
        raise ValidationError("Bitte wähle ein Familienbild aus.")
    encoded = sanitized_profile_photo(upload)
    photo, _created = FamilyPhoto.objects.get_or_create(
        household=household, school_class=school_class, defaults={"uploaded_by": user}
    )
    previous = photo.image.name if photo.image else ""
    photo.image.save(f"{secrets.token_urlsafe(18)}.webp", ContentFile(encoded), save=False)
    photo.uploaded_by = user
    photo.save()
    photo.subjects.set(selected_people)
    if previous and previous != photo.image.name:
        photo.image.storage.delete(previous)
    AuditEvent.objects.create(
        actor=user,
        action="family.photo.saved",
        target_type="family_photo",
        target_id=str(photo.pk),
        metadata={"subject_count": len(selected_people), "school_class_id": school_class.pk},
    )
    return photo


@transaction.atomic
def remove_family_photo(*, user, photo):
    if not may_manage_family_photo(user, photo.household, photo.school_class):
        raise PermissionDenied
    image_name = photo.image.name
    storage = photo.image.storage
    photo_id = photo.pk
    photo.delete()
    if image_name:
        storage.delete(image_name)
    AuditEvent.objects.create(
        actor=user,
        action="family.photo.removed",
        target_type="family_photo",
        target_id=str(photo_id),
    )
