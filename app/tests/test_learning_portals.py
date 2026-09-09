import pytest
from django.urls import reverse

from klasse5e.portal_adapters.models import PortalAdapter, PortalAdapterModule


@pytest.mark.django_db
def test_learning_portals_lists_enabled_school_portals(client, guardian, school_class):
    adapter = PortalAdapter.objects.create(
        provider=PortalAdapter.Provider.MUNDO,
        name="MUNDO",
        base_url="https://mundo.schule/",
        is_enabled=True,
    )
    adapter.schools.add(school_class.school)
    PortalAdapterModule.objects.create(
        adapter=adapter,
        key="material-search",
        label="Materialsuche",
        description="Offene Bildungsmaterialien finden.",
        is_enabled=True,
    )
    client.force_login(guardian)

    menu = client.get(reverse("ui-more"), secure=True)
    page = client.get(reverse("ui-learning-portals"), secure=True)

    assert menu.status_code == 200
    assert "Lernportale" in menu.content.decode()
    assert page.status_code == 200
    body = page.content.decode()
    assert "MUNDO" in body
    assert "Materialsuche" in body
    assert 'href="https://mundo.schule/"' in body


@pytest.mark.django_db
def test_learning_portals_hides_disabled_modules(client, guardian, school_class):
    adapter = PortalAdapter.objects.create(
        provider=PortalAdapter.Provider.MUNDO,
        name="MUNDO",
        base_url="https://mundo.schule/",
        is_enabled=True,
    )
    adapter.schools.add(school_class.school)
    PortalAdapterModule.objects.create(
        adapter=adapter,
        key="material-search",
        label="Materialsuche",
        is_enabled=False,
    )
    client.force_login(guardian)

    body = client.get(reverse("ui-learning-portals"), secure=True).content.decode()

    assert "Noch keine Lernportale freigegeben" in body
    assert "MUNDO öffnen" not in body
