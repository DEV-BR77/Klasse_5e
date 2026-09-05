from datetime import date
from uuid import uuid4

import pytest
from django.contrib.auth.hashers import make_password
from django.core.management import call_command

from klasse5e.core.models import (
    AuditEvent,
    ClassMembership,
    FamilyAccessCode,
    FamilyChildAccount,
    FamilyRegistrationRequest,
    Household,
    Person,
    StudentProfile,
    UserAccount,
)


@pytest.mark.django_db
def test_repair_family_identity_links_joins_only_an_unambiguous_child(
    school_class, admin_user
):
    guardian = UserAccount.objects.create_user(
        email="parent@example.test", password="Safe-Test-Password-123!"
    )
    guardian_person = Person.objects.create(
        user=guardian, first_name="Erika", last_name="Beispiel"
    )
    child_login = UserAccount.objects.create_user(
        email="child@example.test", password="Child-Safe-Password-123!"
    )
    child = Person.objects.create(first_name="Kim", last_name="Beispiel")
    StudentProfile.objects.create(person=child)
    ClassMembership.objects.create(
        school_class=school_class,
        person=child,
        valid_from=date(2026, 8, 1),
        status="active",
    )
    household = Household.objects.create(label="Familie Beispiel")
    household.members.add(guardian_person)
    access_code, _token = FamilyAccessCode.issue(
        batch_id=uuid4(),
        serial_number=1,
        school_class=school_class,
        created_by=admin_user,
    )
    family = FamilyRegistrationRequest.objects.create(
        access_code=access_code,
        household_label="Familie Beispiel",
        household=household,
        children=[{"first_name": "Kim", "last_name": "Beispiel"}],
        status="completed",
    )
    FamilyChildAccount.objects.create(
        family_request=family,
        first_name="Kim",
        last_name="Beispiel",
        email="child@example.test",
        password_hash=make_password("Child-Safe-Password-123!"),
        activated_user=child_login,
    )

    call_command("repair_family_identity_links")
    child.refresh_from_db()
    assert child.user_id is None
    assert not household.members.filter(pk=child.pk).exists()

    call_command("repair_family_identity_links", "--apply")
    child.refresh_from_db()
    assert child.user_id == child_login.pk
    assert household.members.filter(pk=child.pk).exists()
    assert AuditEvent.objects.filter(
        action="family.child_identity.repaired", target_id=str(child.pk)
    ).exists()
