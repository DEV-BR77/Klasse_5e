from datetime import date

import pytest
from allauth.mfa.models import Authenticator
from cryptography.fernet import Fernet
from django.test import override_settings
from django.utils import timezone

from klasse5e.core.models import (
    ClassMembership,
    GuardianChildRelationship,
    Person,
    Role,
    RoleAssignment,
    School,
    SchoolClass,
)
from klasse5e.portal_adapters.models import (
    ChildModuleConnection,
    PortalAdapter,
    PortalAdapterModule,
)
from klasse5e.webuntis.models import WebUntisConnection


@pytest.mark.django_db
def test_admin_can_create_mensamax_adapter_with_weekly_menu_module(client, admin_user, school):
    client.force_login(admin_user)

    response = client.post(
        "/verwaltung/adapter/",
        {"provider": "mensamax", "school_id": school.pk, "name": "MensaMax"},
        secure=True,
    )

    adapter = PortalAdapter.objects.get(school=school, provider="mensamax")
    assert response.status_code == 302
    assert adapter.base_url == "https://app.mensamax.de/"
    assert list(adapter.modules.values_list("key", flat=True)) == ["weekly-meal-plan"]

    response = client.post(
        f"/verwaltung/adapter/{adapter.pk}/",
        {
            "action": "save_module",
            "module_id": adapter.modules.get().pk,
            "is_enabled": "on",
            "configuration_note": "Klassen 5 und 6 anzeigen",
        },
        secure=True,
    )
    module = PortalAdapterModule.objects.get(adapter=adapter)
    assert response.status_code == 302
    assert module.is_enabled is True
    assert module.status == PortalAdapterModule.Status.READY
    assert module.configuration_note == "Klassen 5 und 6 anzeigen"


@pytest.mark.django_db
def test_admin_can_create_dsb_and_wobila_adapters_with_independent_modules(client, admin_user, school):
    client.force_login(admin_user)
    for provider in ("dsbmobile", "mundo", "wirlernenonline", "wobila-bbb", "wobila-mail"):
        response = client.post(
            "/verwaltung/adapter/",
            {"provider": provider, "school_id": school.pk},
            secure=True,
        )
        assert response.status_code == 302

    dsb = PortalAdapter.objects.get(school=school, provider="dsbmobile")
    assert set(dsb.modules.values_list("key", flat=True)) == {"substitutions", "notices"}
    assert PortalAdapter.objects.get(school=school, provider="mundo").modules.get().key == "material-search"
    assert PortalAdapter.objects.get(school=school, provider="wobila-bbb").modules.get().key == "meeting-launcher"
    assert PortalAdapter.objects.get(school=school, provider="wobila-mail").modules.get().key == "webmail-launcher"


@pytest.mark.django_db
def test_adapter_management_is_hidden_from_guardians(client, guardian):
    client.force_login(guardian)
    assert client.get("/verwaltung/adapter/", secure=True).status_code == 404


@pytest.mark.django_db
def test_school_admin_cannot_read_or_change_another_schools_adapter(
    client, guardian, school, year
):
    other_school = School.objects.create(name="Andere Schule", slug="andere-schule")
    own_adapter = PortalAdapter.objects.create(provider="mensamax", name="Eigene", school=school)
    foreign_adapter = PortalAdapter.objects.create(
        provider="mensamax", name="Fremde", school=other_school
    )
    RoleAssignment.objects.create(user=guardian, role=Role.SCHOOL_ADMIN, school=school)
    Authenticator.objects.create(
        user=guardian,
        type=Authenticator.Type.TOTP,
        data={"secret": "synthetic-test-only"},
    )
    client.force_login(guardian)

    listing = client.get("/verwaltung/adapter/", secure=True)
    assert listing.status_code == 200
    assert "Eigene" in listing.content.decode()
    assert "Fremde" not in listing.content.decode()
    assert client.get(f"/verwaltung/adapter/{foreign_adapter.pk}/", secure=True).status_code == 404
    assert client.post(
        f"/verwaltung/adapter/{foreign_adapter.pk}/", {"action": "delete_adapter"}, secure=True
    ).status_code == 404
    assert PortalAdapter.objects.filter(pk=own_adapter.pk).exists()
    assert PortalAdapter.objects.filter(pk=foreign_adapter.pk).exists()


@pytest.mark.django_db
def test_school_admin_can_limit_a_module_to_selected_classes(client, admin_user, school, school_class):
    client.force_login(admin_user)
    response = client.post(
        "/verwaltung/adapter/",
        {"provider": "webuntis", "school_id": school.pk},
        secure=True,
    )
    assert response.status_code == 302
    adapter = PortalAdapter.objects.get(school=school, provider="webuntis")
    module = adapter.modules.get(key="timetable")

    response = client.post(
        f"/verwaltung/adapter/{adapter.pk}/",
        {
            "action": "save_module",
            "module_id": module.pk,
            "is_enabled": "on",
            "requires_child_credentials": "on",
            "available_to_classes": [school_class.pk],
        },
        secure=True,
    )
    assert response.status_code == 302
    module.refresh_from_db()
    assert module.is_enabled is True
    assert module.requires_child_credentials is True
    assert list(module.available_to_classes.all()) == [school_class]


@pytest.mark.django_db
def test_webuntis_adapter_only_requests_its_school_url(client, admin_user, school):
    adapter = PortalAdapter.objects.create(
        school=school,
        provider="webuntis",
        name="WebUntis",
        base_url="https://thgwob.webuntis.com/",
        project_identifier="legacy-project",
        institution_identifier="legacy-school",
        school_number="legacy-number",
    )
    client.force_login(admin_user)

    page = client.get(f"/verwaltung/adapter/{adapter.pk}/", secure=True)

    assert page.status_code == 200
    body = page.content.decode()
    assert "Für WebUntis genügt die Adresse der jeweiligen Schule" in body
    assert 'name="project_identifier"' not in body
    assert 'name="institution_identifier"' not in body
    assert 'name="school_number"' not in body

    response = client.post(
        f"/verwaltung/adapter/{adapter.pk}/",
        {"action": "save_adapter", "base_url": "https://heinrich-nordhoff.webuntis.com/"},
        secure=True,
    )

    assert response.status_code == 302
    adapter.refresh_from_db()
    assert adapter.base_url == "https://heinrich-nordhoff.webuntis.com/"
    assert adapter.project_identifier == "legacy-project"
    assert adapter.institution_identifier == "legacy-school"
    assert adapter.school_number == "legacy-number"


@pytest.mark.django_db
@override_settings(WEBUNTIS_CREDENTIAL_ENCRYPTION_KEY=Fernet.generate_key().decode())
def test_guardian_can_only_activate_school_approved_modules_for_own_child(
    client, guardian, school_class
):
    child = Person.objects.create(first_name="Mila", last_name="Beispiel")
    ClassMembership.objects.create(
        person=child,
        school_class=school_class,
        valid_from=date(2026, 8, 1),
        status="active",
    )
    relationship = GuardianChildRelationship.objects.create(
        guardian_person=guardian.person,
        student_person=child,
        relationship_type="father",
        is_legal_guardian=True,
        may_view_student_profile=True,
        may_manage_profile=True,
        valid_from=date(2026, 8, 1),
        status="verified",
        verified_by=guardian,
        verified_at=timezone.now(),
    )
    adapter = PortalAdapter.objects.create(
        school=school_class.school,
        provider="webuntis",
        name="Schuldaten-Zugang",
        is_enabled=True,
        base_url="https://thgwob.webuntis.com/",
    )
    allowed_module = PortalAdapterModule.objects.create(
        adapter=adapter,
        key="timetable",
        label="Stundenplan",
        is_enabled=True,
        requires_child_credentials=True,
    )
    allowed_module.available_to_classes.add(school_class)
    hidden_module = PortalAdapterModule.objects.create(
        adapter=adapter,
        key="exams",
        label="Prüfungen",
        is_enabled=True,
    )
    other_class = SchoolClass.objects.create(
        school=school_class.school,
        school_year=school_class.school_year,
        name="Synthetische 6e",
        code="6e",
    )
    hidden_module.available_to_classes.add(other_class)

    client.force_login(guardian)
    assert client.get(f"/mehr/webuntis/?student={child.pk}", secure=True).status_code == 404
    family = client.get("/mehr/familie/", secure=True)
    assert family.status_code == 200
    module_labels = [
        module_row["module"].label
        for row in family.context["relationship_rows"]
        for module_row in row["modules"]
    ]
    assert "Stundenplan" in module_labels
    assert "Prüfungen" not in module_labels

    response = client.post(
        "/mehr/familie/",
        {
            "relationship_id": relationship.pk,
            "module_id": allowed_module.pk,
            "enabled": "on",
        },
        secure=True,
    )
    assert response.status_code == 302
    connection = ChildModuleConnection.objects.get(student=child, module=allowed_module)
    assert connection.is_enabled is True
    assert connection.connection_state == ChildModuleConnection.ConnectionState.CREDENTIALS_NEEDED

    # A direct concrete-adapter URL remains unavailable until the parent made
    # the personal choice above, then stores credentials only for this child.
    response = client.post(
        f"/mehr/webuntis/?student={child.pk}",
        {
            "username": "synthetic-user",
            "password": "synthetic-password",
            "return_to": "family",
        },
        secure=True,
    )
    assert response.status_code == 302
    assert response.url == f"/mehr/familie/?tab=modules&child={relationship.pk}"
    assert WebUntisConnection.objects.filter(user=guardian, student=child).exists()
    connection.refresh_from_db()
    assert connection.connection_state == ChildModuleConnection.ConnectionState.CONNECTED

    family = client.get(
        f"/mehr/familie/?tab=modules&child={relationship.pk}", secure=True
    )
    body = family.content.decode()
    assert body.count("WebUntis-Zugang für Mila") == 1
    assert 'name="username"' in body
    assert 'name="password"' in body
    assert "Zugangsdaten sind gespeichert" in body
    assert "Zugangsdaten pflegen" not in body

    adapter.is_enabled = False
    adapter.save(update_fields=["is_enabled"])
    assert client.get(f"/mehr/webuntis/?student={child.pk}", secure=True).status_code == 404

    response = client.post(
        "/mehr/familie/",
        {
            "relationship_id": relationship.pk,
            "module_id": hidden_module.pk,
            "enabled": "on",
        },
        secure=True,
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_module_quick_toggle_preserves_advanced_settings(
    client, admin_user, school, school_class
):
    adapter = PortalAdapter.objects.create(
        school=school,
        provider=PortalAdapter.Provider.WEBUNTIS,
        name="WebUntis",
        is_enabled=True,
        requires_child_credentials=True,
    )
    module = PortalAdapterModule.objects.create(
        adapter=adapter,
        key="homework",
        label="Hausaufgaben",
        description="Aufgaben und Fälligkeiten abrufen.",
        is_enabled=True,
        requires_child_credentials=True,
        configuration_note="Nur für die Pilotklasse",
    )
    module.available_to_classes.add(school_class)
    client.force_login(admin_user)

    page = client.get(f"/verwaltung/adapter/{adapter.pk}/", secure=True)
    body = page.content.decode()
    assert "portal-module-list" in body
    assert "Aufgaben und Fälligkeiten abrufen." in body
    assert "Weitere Einstellungen" in body

    response = client.post(
        f"/verwaltung/adapter/{adapter.pk}/",
        {
            "action": "toggle_module",
            "module_id": module.pk,
        },
        secure=True,
    )

    assert response.status_code == 302
    module.refresh_from_db()
    assert module.is_enabled is False
    assert module.requires_child_credentials is True
    assert module.configuration_note == "Nur für die Pilotklasse"
    assert list(module.available_to_classes.all()) == [school_class]
