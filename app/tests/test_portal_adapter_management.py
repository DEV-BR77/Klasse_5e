from datetime import date

import pytest
from django.utils import timezone

from klasse5e.core.models import ClassMembership, GuardianChildRelationship, Person, SchoolClass
from klasse5e.portal_adapters.models import (
    ChildModuleConnection,
    PortalAdapter,
    PortalAdapterModule,
)


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
