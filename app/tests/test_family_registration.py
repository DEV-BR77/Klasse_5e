from uuid import uuid4

import pytest
from django.contrib.auth.hashers import make_password
from django.core import mail
from django.test import override_settings
from django.utils import timezone

from klasse5e.core.models import (
    ActivationGrant,
    ClassMembership,
    FamilyAccessCode,
    FamilyChildAccount,
    FamilyRegistrationRequest,
    GuardianChildRelationship,
    Household,
    Invitation,
    Person,
    RegistrationApplication,
    RelationshipStatus,
    RelationshipType,
    Role,
    RoleAssignment,
    UserAccount,
)
from klasse5e.core.registration import activate, create_application


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    WAGTAILADMIN_BASE_URL="https://5e.klassid.de",
)
def test_family_code_refreshes_unverified_application_and_allows_empty_second_adult(
    client, school_class, admin_user
):
    existing, old_email_token = create_application(
        email="family@example.test",
        first_name="Alter",
        last_name="Versuch",
        password="Old-Safe-Password-123!",
    )
    access_code, token = FamilyAccessCode.issue(
        batch_id=uuid4(),
        serial_number=1,
        school_class=school_class,
        created_by=admin_user,
    )

    response = client.post(
        f"/familie/start/{token}/",
        {
            "first_name": "Erika",
            "last_name": "Beispiel",
            "email": "family@example.test",
            "password": "New-Safe-Password-123!",
            "adult_2_first_name": "",
            "adult_2_last_name": "",
            "adult_2_email": "",
            "child_1_first_name": "Kim",
            "child_1_last_name": "Beispiel",
            "child_1_email": "kim@example.test",
            "child_1_password": "Child-Safe-Password-123!",
            "child_2_first_name": "",
            "child_2_last_name": "",
            "household_label": "Familie Beispiel",
            "privacy_ack": "yes",
        },
    )

    assert response.status_code == 202
    assert RegistrationApplication.objects.filter(email="family@example.test").count() == 1
    existing.refresh_from_db()
    access_code.refresh_from_db()
    assert existing.first_name == "Erika"
    assert existing.family_request_id is not None
    assert access_code.submitted_at is not None
    family = FamilyRegistrationRequest.objects.get(pk=existing.family_request_id)
    assert family.additional_adults == []
    assert family.children == [{"first_name": "Kim", "last_name": "Beispiel"}]
    assert FamilyChildAccount.objects.filter(
        family_request=family, email="kim@example.test"
    ).exists()
    assert len(mail.outbox) == 1
    assert old_email_token not in mail.outbox[0].body


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_family_form_keeps_safe_fields_after_validation_error(client, school_class, admin_user):
    _access_code, token = FamilyAccessCode.issue(
        batch_id=uuid4(),
        serial_number=1,
        school_class=school_class,
        created_by=admin_user,
    )
    response = client.post(
        f"/familie/start/{token}/",
        {
            "first_name": "Erika",
            "last_name": "Beispiel",
            "email": "family@example.test",
            "password": "New-Safe-Password-123!",
            "child_1_first_name": "Kim",
            "child_1_last_name": "",
            "child_1_email": "kim@example.test",
            "child_1_password": "Child-Safe-Password-123!",
            "privacy_ack": "yes",
        },
    )
    html = response.content.decode()
    assert response.status_code == 400
    assert "Bitte gib für Kind 1 Vorname, Nachname, E-Mail-Adresse" in html
    assert 'value="Erika"' in html
    assert 'value="family@example.test"' in html
    assert 'value="New-Safe-Password-123!"' not in html


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_activation_links_existing_father_without_duplicate_account(
    school, school_class, admin_user
):
    father = UserAccount.objects.create_user(
        email="father@example.test", password="Safe-Test-Password-123!"
    )
    father_person = Person.objects.create(
        user=father, first_name="Adrian Bjorn", last_name="Beispiel"
    )
    access_code, _token = FamilyAccessCode.issue(
        batch_id=uuid4(),
        serial_number=1,
        school_class=school_class,
        created_by=admin_user,
        max_uses=2,
    )
    access_code.existing_guardian = father
    access_code.existing_guardian_relationship_type = RelationshipType.FATHER
    access_code.save(update_fields=["existing_guardian", "existing_guardian_relationship_type"])
    family = FamilyRegistrationRequest.objects.create(
        access_code=access_code,
        household_label="Familie Beispiel",
        additional_adults=[],
        children=[{"first_name": "Kim", "last_name": "Beispiel"}],
    )
    FamilyChildAccount.objects.create(
        family_request=family,
        first_name="Kim",
        last_name="Beispiel",
        email="kim@example.test",
        password_hash=make_password("Child-Safe-Password-123!"),
    )
    application, _email_token = create_application(
        email="mother@example.test",
        first_name="Erika",
        last_name="Beispiel",
        password="Safe-Test-Password-123!",
    )
    application.family_request = family
    application.school = school
    application.school_class = school_class
    application.reviewed_by = admin_user
    application.reviewed_at = timezone.now()
    application.email_verified_at = timezone.now()
    application.status = RegistrationApplication.Status.APPROVED
    application.save()
    _grant, activation_token = ActivationGrant.issue(application)

    mother = activate(activation_token)

    assert mother is not None
    assert UserAccount.objects.filter(email="father@example.test").count() == 1
    family.refresh_from_db()
    household = Household.objects.get(pk=family.household_id)
    child = household.members.get(studentprofile__isnull=False)
    assert set(household.members.values_list("pk", flat=True)) == {
        mother.person.pk,
        father_person.pk,
        child.pk,
    }
    assert ClassMembership.objects.filter(
        school_class=school_class, person=father_person, status="active"
    ).exists()
    assert RoleAssignment.objects.filter(
        user=father,
        school_class=school_class,
        role=Role.GUARDIAN,
        active=True,
    ).exists()
    relationship = GuardianChildRelationship.objects.get(
        guardian_person=father_person, student_person=child
    )
    assert relationship.relationship_type == RelationshipType.FATHER
    assert relationship.status == RelationshipStatus.VERIFIED
    assert relationship.is_legal_guardian
    assert Invitation.objects.filter(email="father@example.test").count() == 0
    access_code.refresh_from_db()
    assert access_code.existing_guardian is None
    child_user = UserAccount.objects.get(email="kim@example.test")
    assert child.user == child_user
    assert child_user.check_password("Child-Safe-Password-123!")
    assert not RoleAssignment.objects.filter(user=child_user, role=Role.GUARDIAN).exists()


@pytest.mark.django_db
def test_reusable_family_code_accepts_configured_number_of_submissions(school_class, admin_user):
    access_code, token = FamilyAccessCode.issue(
        batch_id=uuid4(),
        serial_number=1,
        school_class=school_class,
        created_by=admin_user,
        max_uses=2,
    )

    assert FamilyAccessCode.resolve(token) == access_code
    access_code.use_count = 1
    access_code.submitted_at = timezone.now()
    access_code.save(update_fields=["use_count", "submitted_at"])
    assert FamilyAccessCode.resolve(token) == access_code
    access_code.use_count = 2
    access_code.save(update_fields=["use_count"])
    assert FamilyAccessCode.resolve(token) is None


@pytest.mark.django_db
def test_googlemail_alias_is_normalized_to_gmail_for_login():
    application, _token = create_application(
        email="Example.User@googlemail.com",
        first_name="Erika",
        last_name="Beispiel",
        password="Safe-Test-Password-123!",
    )

    assert application.email == "example.user@gmail.com"
