from datetime import date

import pytest
from django.core.management import call_command

from klasse5e.core.models import Role, RoleAssignment, School, SchoolClass, SchoolYear, UserAccount


@pytest.mark.django_db
def test_consolidates_legacy_thg_school_without_losing_roles(capsys):
    year = SchoolYear.objects.create(
        label="2026/27", starts_on=date(2026, 8, 1), ends_on=date(2027, 7, 31), is_active=True
    )
    source = School.objects.create(
        name="Theodor-Heuss-Gymnasium", short_name="THG", slug="standard-schule"
    )
    target = School.objects.create(
        name="Theodor-Heuss-Gymnasium Wolfsburg", short_name="THG", slug="thg-wolfsburg"
    )
    legacy = SchoolClass.objects.create(school=source, name="5e", code="5e", school_year=year)
    active = SchoolClass.objects.create(school=target, name="5e", code="5e", school_year=year)
    test_class = SchoolClass.objects.create(
        school=source,
        name="Synthetic Phase5",
        code="synthetic-phase5",
        school_year=year,
        status="active",
    )
    user = UserAccount.objects.create_user("guardian@example.test", "Testpasswort!123")
    RoleAssignment.objects.create(user=user, school_class=legacy, role=Role.GUARDIAN)
    RoleAssignment.objects.create(user=user, school_class=active, role=Role.GUARDIAN)

    call_command("consolidate_thg_school")
    assert "Keine Daten geändert" in capsys.readouterr().out
    assert School.objects.filter(slug="standard-schule").exists()

    call_command("consolidate_thg_school", "--apply")

    assert not School.objects.filter(slug="standard-schule").exists()
    target.refresh_from_db()
    assert (target.postal_code, target.address, target.federal_state) == (
        "38440",
        "Martin-Luther-Straße 23",
        "Niedersachsen",
    )
    assert SchoolClass.objects.filter(pk=legacy.pk).exists() is False
    assert RoleAssignment.objects.filter(user=user, school_class=active, role=Role.GUARDIAN).count() == 1
    test_class.refresh_from_db()
    assert (test_class.school_id, test_class.status, test_class.code) == (
        target.id,
        "archived",
        "test-phase5",
    )
