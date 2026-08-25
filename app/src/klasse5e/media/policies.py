from django.utils import timezone

from klasse5e.core.models import ClassMembership, ConsentType, Role
from klasse5e.core.policies import active_roles, consent_state, has_active_membership

PHOTO_POLICY_VERSION = "photo-policy-v1"


def may_access_gallery(user, gallery):
    if (
        gallery.status != "published"
        or not gallery.retention_until
        or gallery.retention_until <= timezone.now()
    ):
        return False
    if has_active_membership(user, gallery.school_class):
        return True
    return bool(
        active_roles(user, gallery.school_class)
        & {Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN, Role.TEACHER, Role.MODERATOR}
    )


def may_manage_gallery(user, gallery):
    roles = active_roles(user, gallery.school_class)
    if roles & {Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN, Role.EDITOR}:
        return True
    return bool(
        gallery.event_id
        and Role.ORGANIZER in roles
        and gallery.event.organizers.filter(id=user.id).exists()
    )


def may_upload(user, gallery, accepted_rules=False):
    return accepted_rules and gallery.upload_allowed and may_access_gallery(user, gallery)


def _consent(key, person):
    consent_type = ConsentType.objects.filter(key=key).first()
    return bool(consent_type and consent_state(consent_type, person) == "allowed")


def photo_consent_result(photo, *, download=False):
    declarations = list(photo.subject_declarations.select_related("person"))
    if not declarations or any(item.kind == "unclear" for item in declarations):
        return False, "unclear_person"
    for item in declarations:
        if item.kind == "known":
            if not item.person_id or item.status != "confirmed":
                return False, "unconfirmed_subject"
            if not ClassMembership.objects.filter(
                person=item.person, school_class=photo.gallery.school_class, status="active"
            ).exists():
                return False, "subject_outside_class"
            if not _consent("event-photos", item.person):
                return False, "missing_photo_consent"
            if not _consent("manual-photo-assignment", item.person):
                return False, "missing_assignment_consent"
            if download and not _consent("photo-download", item.person):
                return False, "missing_download_consent"
    return True, "allowed"


def may_view_photo(user, photo):
    allowed, _ = photo_consent_result(photo)
    return photo.status == "published" and may_access_gallery(user, photo.gallery) and allowed


def may_download_photo(user, photo):
    allowed, _ = photo_consent_result(photo, download=True)
    return (
        may_view_photo(user, photo)
        and photo.gallery.download_allowed
        and photo.download_allowed
        and allowed
    )
