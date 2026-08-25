import io
from datetime import date, timedelta

import pytest
from allauth.mfa.models import Authenticator
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.utils import timezone
from PIL import Image

from klasse5e.core.models import (
    ClassMembership,
    ConsentDecision,
    ConsentTextVersion,
    ConsentType,
    Person,
    RoleAssignment,
    UserAccount,
)
from klasse5e.events.models import Event
from klasse5e.media.models import Gallery, Photo, PhotoReport, PhotoSubjectDeclaration
from klasse5e.media.policies import (
    may_download_photo,
    may_manage_gallery,
    may_view_photo,
    photo_consent_result,
)
from klasse5e.media.services import (
    create_photo,
    decide_photo,
    delete_photo_files,
    process_upload,
    safe_original_name,
)


def image_file(fmt="JPEG", name="synthetic.jpg", size=(40, 30), exif=False, content_type=None):
    data = io.BytesIO()
    image = Image.new("RGB", size, (20, 120, 180))
    metadata = Image.Exif()
    if exif:
        metadata[274] = 6
        metadata[305] = "synthetic-camera"
    image.save(data, fmt, exif=metadata)
    return SimpleUploadedFile(
        name, data.getvalue(), content_type=content_type or f"image/{fmt.lower()}"
    )


@pytest.fixture
def gallery(db, guardian, school_class, year, settings):
    settings.MEDIA_ROOT = settings.BASE_DIR / ".test-runtime" / "phase5-media"
    return Gallery.objects.create(
        school_class=school_class,
        school_year=year,
        title="Synthetische Galerie",
        status="published",
        upload_allowed=True,
        retention_until=timezone.now() + timedelta(days=30),
        created_by=guardian,
        published_at=timezone.now(),
    )


@pytest.fixture
def moderator(db, school_class):
    user = UserAccount.objects.create_user("photo-moderator@example.test", "Pass-123456789!")
    person = Person.objects.create(user=user, first_name="Mod", last_name="Synthetic")
    ClassMembership.objects.create(
        school_class=school_class, person=person, valid_from=date(2026, 8, 1)
    )
    RoleAssignment.objects.create(user=user, school_class=school_class, role="moderator")
    Authenticator.objects.create(
        user=user, type=Authenticator.Type.TOTP, data={"secret": "synthetic-test-only"}
    )
    return user


def add_decision(key, person, decider, decision="granted"):
    consent = ConsentType.objects.create(
        key=key, label=key, category="photo", purpose="Test", recipients="Klasse"
    )
    text = ConsentTextVersion.objects.create(
        consent_type=consent,
        version="draft-1",
        text="Fachlicher Entwurf",
        effective_from=timezone.now(),
    )
    return ConsentDecision.objects.create(
        consent_type=consent,
        text_version=text,
        subject_person=person,
        deciding_person=decider,
        decision=decision,
    )


@pytest.mark.django_db
def test_gallery_event_must_match_class(gallery, guardian, year):
    from klasse5e.core.models import SchoolClass

    other = SchoolClass.objects.create(name="Other", school_year=year)
    event = Event.objects.create(
        school_class=other,
        school_year=year,
        title="Other",
        description="",
        starts_at=timezone.now(),
        ends_at=timezone.now() + timedelta(hours=1),
        location="",
        change_deadline=timezone.now(),
    )
    gallery.event = event
    with pytest.raises(ValidationError):
        gallery.full_clean()


@pytest.mark.django_db
def test_organizer_only_manages_own_event(gallery, guardian, year):
    event = Event.objects.create(
        school_class=gallery.school_class,
        school_year=year,
        title="Own",
        description="",
        starts_at=timezone.now(),
        ends_at=timezone.now() + timedelta(hours=1),
        location="",
        change_deadline=timezone.now() + timedelta(days=1),
    )
    event.organizers.add(guardian)
    gallery.event = event
    gallery.save()
    RoleAssignment.objects.create(
        user=guardian, school_class=gallery.school_class, role="organizer"
    )
    assert may_manage_gallery(guardian, gallery)
    event.organizers.clear()
    assert not may_manage_gallery(guardian, gallery)


@pytest.mark.django_db
@pytest.mark.parametrize("fmt,name", [("JPEG", "valid.jpg"), ("PNG", "valid.png")])
def test_upload_reencodes_supported_images_and_strips_metadata(gallery, guardian, fmt, name):
    photo = create_photo(
        gallery=gallery, uploader=guardian, upload=image_file(fmt, name, exif=True)
    )
    assert photo.status == "pending" and photo.original_name == name
    for field in [photo.display_file, photo.thumbnail_file]:
        with Image.open(field.path) as image:
            assert not image.getexif() and image.width <= 480


@pytest.mark.django_db
def test_extension_and_mime_are_not_trusted(gallery, guardian):
    photo = create_photo(
        gallery=gallery,
        uploader=guardian,
        upload=image_file("PNG", "fake.jpg", content_type="text/plain"),
    )
    assert photo.content_type == "image/jpeg"
    assert photo.display_file.name.endswith(".jpg")


@pytest.mark.django_db
def test_invalid_large_and_pixel_limit(gallery, guardian, settings):
    with pytest.raises(ValidationError):
        process_upload(SimpleUploadedFile("bad.jpg", b"broken", content_type="image/jpeg"))
    settings.GALLERY_MAX_UPLOAD_BYTES = 3
    with pytest.raises(ValidationError):
        process_upload(image_file())
    settings.GALLERY_MAX_UPLOAD_BYTES = 20 * 1024 * 1024
    settings.GALLERY_MAX_PIXELS = 10
    with pytest.raises(ValidationError):
        process_upload(image_file())
    assert safe_original_name("../../evil name.jpg") == "evil_name.jpg"


@pytest.mark.django_db
def test_unknown_subject_blocks_moderation(gallery, guardian, moderator):
    photo = create_photo(gallery=gallery, uploader=guardian, upload=image_file())
    PhotoSubjectDeclaration.objects.create(photo=photo, kind="unclear", declared_by=guardian)
    with pytest.raises(ValidationError):
        decide_photo(photo, moderator, "publish")


@pytest.mark.django_db
def test_all_students_need_current_photo_and_assignment_consent(gallery, guardian, moderator):
    students = []
    for index in range(2):
        person = Person.objects.create(first_name=f"Student{index}", last_name="Synthetic")
        ClassMembership.objects.create(
            school_class=gallery.school_class, person=person, valid_from=date(2026, 8, 1)
        )
        students.append(person)
    photo = create_photo(gallery=gallery, uploader=guardian, upload=image_file())
    for person in students:
        PhotoSubjectDeclaration.objects.create(
            photo=photo,
            person=person,
            kind="known",
            declared_by=guardian,
            confirmed_by=moderator,
            status="confirmed",
            confirmed_at=timezone.now(),
        )
    assert photo_consent_result(photo)[0] is False
    for key in ["event-photos", "manual-photo-assignment"]:
        consent = ConsentType.objects.create(
            key=key, label=key, category="photo", purpose="Test", recipients="Klasse"
        )
        text = ConsentTextVersion.objects.create(
            consent_type=consent, version="draft-1", text="Draft", effective_from=timezone.now()
        )
        for person in students:
            ConsentDecision.objects.create(
                consent_type=consent,
                text_version=text,
                subject_person=person,
                deciding_person=guardian.person,
                decision="granted",
            )
    decide_photo(photo, moderator, "publish")
    photo.refresh_from_db()
    assert photo.status == "published"


@pytest.mark.django_db
def test_download_default_off_and_consent_withdrawal_hides(gallery, guardian, moderator):
    photo = create_photo(gallery=gallery, uploader=guardian, upload=image_file())
    PhotoSubjectDeclaration.objects.create(
        photo=photo, kind="none", declared_by=guardian, confirmed_by=moderator, status="confirmed"
    )
    decide_photo(photo, moderator, "publish")
    assert may_view_photo(guardian, photo) and not may_download_photo(guardian, photo)
    gallery.download_allowed = True
    gallery.save()
    photo.download_allowed = True
    photo.save()
    assert may_download_photo(guardian, photo)


@pytest.mark.django_db
def test_known_subject_consent_withdrawal_immediately_blocks(gallery, guardian, moderator):
    student = Person.objects.create(first_name="Consent", last_name="Synthetic")
    ClassMembership.objects.create(
        school_class=gallery.school_class, person=student, valid_from=date(2026, 8, 1)
    )
    decisions = []
    for key in ["event-photos", "manual-photo-assignment"]:
        decisions.append(add_decision(key, student, guardian.person))
    photo = create_photo(gallery=gallery, uploader=guardian, upload=image_file())
    PhotoSubjectDeclaration.objects.create(
        photo=photo,
        person=student,
        kind="known",
        declared_by=guardian,
        confirmed_by=moderator,
        status="confirmed",
        confirmed_at=timezone.now(),
    )
    decide_photo(photo, moderator, "publish")
    assert may_view_photo(guardian, photo)
    decisions[0].revoked_at = timezone.now()
    decisions[0].save(update_fields=["revoked_at"])
    assert not may_view_photo(guardian, photo)


@pytest.mark.django_db
def test_upload_batch_and_moderator_permissions(client, gallery, guardian, moderator, settings):
    client.force_login(guardian)
    response = client.post(
        f"/galleries/{gallery.id}/upload/",
        {"accepted_rules": "yes", "subject_kind": "none", "photos": [image_file(name="one.jpg")]},
    )
    assert response.status_code == 201
    photo = Photo.objects.get(id=response.json()["photos"][0])
    assert photo.status == "pending"
    assert client.post(f"/photos/{photo.id}/moderate/", {"decision": "publish"}).status_code == 404
    client.force_login(moderator)
    declaration = photo.subject_declarations.get()
    declaration.status = "confirmed"
    declaration.confirmed_by = moderator
    declaration.save()
    assert client.post(f"/photos/{photo.id}/moderate/", {"decision": "publish"}).status_code == 204
    settings.GALLERY_MAX_BATCH = 1
    client.force_login(guardian)
    response = client.post(
        f"/galleries/{gallery.id}/upload/",
        {
            "accepted_rules": "yes",
            "subject_kind": "none",
            "photos": [image_file(name="a.jpg"), image_file(name="b.jpg")],
        },
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_protected_delivery_idor_report_and_withdraw(client, gallery, guardian, moderator, year):
    photo = create_photo(gallery=gallery, uploader=guardian, upload=image_file())
    PhotoSubjectDeclaration.objects.create(
        photo=photo, kind="none", declared_by=guardian, confirmed_by=moderator, status="confirmed"
    )
    decide_photo(photo, moderator, "publish")
    assert client.get(f"/photos/{photo.id}/thumbnail/").status_code == 302
    client.force_login(guardian)
    response = client.get(f"/photos/{photo.id}/thumbnail/")
    assert response.status_code == 200 and response["Cache-Control"] == "private, no-store"
    assert client.get(f"/photos/{photo.id}/download/").status_code == 404
    assert client.post(f"/photos/{photo.id}/report/", {"reason": "privacy"}).status_code == 201
    photo.refresh_from_db()
    assert photo.status == "hidden" and PhotoReport.objects.exists()
    assert client.post(f"/photos/{photo.id}/withdraw/").status_code == 204
    other = UserAccount.objects.create_user("foreign@example.test", "Pass-123456789!")
    Person.objects.create(user=other, first_name="Foreign", last_name="Synthetic")
    client.force_login(other)
    assert client.get(f"/photos/{photo.id}/display/").status_code == 404
    assert client.post(f"/photos/{photo.id}/withdraw/").status_code == 404


@pytest.mark.django_db
def test_delete_files_is_idempotent_and_retention_command(gallery, guardian, capsys):
    photo = create_photo(gallery=gallery, uploader=guardian, upload=image_file())
    paths = [photo.display_file.path, photo.thumbnail_file.path, photo.download_file.path]
    delete_photo_files(photo)
    delete_photo_files(photo)
    assert all(not __import__("pathlib").Path(path).exists() for path in paths)
    expired = create_photo(
        gallery=gallery, uploader=guardian, upload=image_file(name="expired.jpg")
    )
    expired.retention_until = timezone.now() - timedelta(seconds=1)
    expired.save()
    call_command("purge_expired_photos", "--delete")
    expired.refresh_from_db()
    assert expired.status == "deleted"


def test_service_worker_does_not_cache_gallery_media():
    script = open("app/src/klasse5e/core/views.py", encoding="utf-8").read()
    assert "/photos/" not in script and "/galleries/" not in script
