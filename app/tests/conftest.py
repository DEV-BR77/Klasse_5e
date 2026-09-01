import os
from datetime import date

os.environ.setdefault("DJANGO_DEBUG", "1")

import pytest
from allauth.mfa.models import Authenticator

from klasse5e.core.models import (
    ClassMembership,
    Person,
    RoleAssignment,
    School,
    SchoolClass,
    SchoolYear,
    UserAccount,
)


@pytest.fixture
def year(db):
    return SchoolYear.objects.create(
        label="2026/27", starts_on=date(2026, 8, 1), ends_on=date(2027, 7, 31), is_active=True
    )


@pytest.fixture
def school(db):
    return School.objects.create(name="Synthetische Schule", slug="synthetische-schule")


@pytest.fixture
def school_class(year, school):
    return SchoolClass.objects.create(school=school, name="Synthetische 5e", school_year=year)


@pytest.fixture
def guardian(db, school_class):
    user = UserAccount.objects.create_user(
        email="guardian@example.test", password="Safe-Test-Password-123!"
    )
    person = Person.objects.create(user=user, first_name="Alex", last_name="Beispiel")
    ClassMembership.objects.create(
        school_class=school_class, person=person, valid_from=date(2026, 8, 1)
    )
    RoleAssignment.objects.create(user=user, school_class=school_class, role="guardian")
    return user


@pytest.fixture
def admin_user(db):
    user = UserAccount.objects.create_user(
        email="admin@example.test", password="Safe-Test-Password-123!"
    )
    Person.objects.create(user=user, first_name="Ada", last_name="Admin")
    RoleAssignment.objects.create(user=user, role="primary_admin")
    Authenticator.objects.create(
        user=user, type=Authenticator.Type.TOTP, data={"secret": "synthetic-test-only"}
    )
    return user
