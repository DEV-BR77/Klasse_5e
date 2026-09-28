import os
from datetime import date
from importlib import import_module

os.environ.setdefault("DJANGO_DEBUG", "1")

import pytest
from allauth.mfa.models import Authenticator
from django.apps import apps as django_apps

from klasse5e.core.models import (
    ClassMembership,
    Person,
    RoleAssignment,
    School,
    SchoolClass,
    SchoolYear,
    UserAccount,
)


@pytest.fixture(autouse=True)
def migration_reference_data(db):
    """Restore migration-seeded reference rows after Django clears a test case.

    The local reusable database contains schema only.  Django deliberately
    clears data between cases, including data that historic migrations seeded.
    Replaying only the reference-data migration functions keeps every case
    equivalent to a newly provisioned portal without rebuilding SQLite.
    """

    for module_name, function_name in (
        ("klasse5e.core.migrations.0003_onboarding_consent_catalog", "seed_consent_catalog"),
        ("klasse5e.core.migrations.0006_portalmodule_portalmoduleoverride", "seed_modules"),
        ("klasse5e.core.migrations.0010_enable_mobility_module", "seed_mobility"),
        ("klasse5e.core.migrations.0011_portaltheme_useraccount_selected_theme", "seed_themes"),
        ("klasse5e.core.migrations.0025_alter_portalconfigurationkey_value_type", "seed_idle_timeout"),
        ("klasse5e.chat.migrations.0002_retention_and_attachments", "seed_categories"),
        ("klasse5e.core.migrations.0039_seed_phase1_role_permissions", "seed_phase1_permissions"),
    ):
        getattr(import_module(module_name), function_name)(django_apps, None)


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
    return SchoolClass.objects.create(
        school=school, name="Synthetische 5e", code="5e", school_year=year
    )


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
