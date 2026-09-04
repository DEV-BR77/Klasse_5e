import pytest

from klasse5e.portal_adapters.models import PortalAdapter, PortalAdapterModule


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
