from io import BytesIO

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from klasse5e.core.family_photos import save_family_photo
from klasse5e.core.models import (
    ClassMembership,
    FamilyPhoto,
    GuardianChildRelationship,
    Household,
    Person,
)
from klasse5e.core.onboarding import record_decision, withdraw_decision


def family_image():
    image = Image.new("RGB", (12, 8), color="#7058d8")
    payload = BytesIO()
    image.save(payload, format="PNG")
    return SimpleUploadedFile("familie.png", payload.getvalue(), content_type="image/png")


@pytest.fixture
def managed_child(guardian):
    child = Person.objects.create(first_name="Mila", last_name="Beispiel")
    GuardianChildRelationship.objects.create(
        guardian_person=guardian.person,
        student_person=child,
        relationship_type="mother",
        is_legal_guardian=True,
        may_view_student_profile=True,
        may_manage_profile=True,
        valid_from=timezone.localdate(),
        status="verified",
        verified_by=guardian,
        verified_at=timezone.now(),
    )
    return child


@pytest.mark.django_db
def test_family_photo_requires_each_subject_consent_and_falls_back_on_withdrawal(
    client, guardian, managed_child, school_class
):
    ClassMembership.objects.create(
        person=managed_child, school_class=school_class, valid_from=timezone.localdate()
    )
    relationship = GuardianChildRelationship.objects.get(student_person=managed_child)
    relationship.may_manage_photo_consents = True
    relationship.save(update_fields=["may_manage_photo_consents"])
    household = Household.objects.create(label="Familie Beispiel")
    household.members.add(guardian.person, managed_child)

    with pytest.raises(ValidationError):
        save_family_photo(
            user=guardian,
            household=household,
            school_class=school_class,
            upload=family_image(),
            subject_ids=[guardian.person.pk, managed_child.pk],
        )

    for person in (guardian.person, managed_child):
        record_decision(
            user=guardian,
            subject=person,
            key="photo_gallery",
            decision="granted",
            source="test",
        )
    photo = save_family_photo(
        user=guardian,
        household=household,
        school_class=school_class,
        upload=family_image(),
        subject_ids=[guardian.person.pk, managed_child.pk],
    )
    assert FamilyPhoto.objects.get(pk=photo.pk).subjects.count() == 2

    client.force_login(guardian)
    family_page = client.get(reverse("ui-family"), secure=True)
    assert family_page.status_code == 200
    assert reverse("family-photo", args=[photo.pk]).encode() in family_page.content
    contacts = client.get(reverse("ui-contacts"), secure=True)
    assert contacts.status_code == 200
    assert reverse("family-photo", args=[photo.pk]).encode() in contacts.content
    assert b"family-initials" not in contacts.content
    image = client.get(reverse("family-photo", args=[photo.pk]), secure=True)
    assert image.status_code == 200
    image.close()

    withdraw_decision(user=guardian, subject=managed_child, key="photo_gallery")
    contacts = client.get(reverse("ui-contacts"), secure=True)
    assert b"family-initials" in contacts.content
    assert client.get(reverse("family-photo", args=[photo.pk]), secure=True).status_code == 404
