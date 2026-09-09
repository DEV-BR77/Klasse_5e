import pytest

from klasse5e.core.models import PortalTheme


@pytest.mark.django_db
def test_theme_management_does_not_offer_removed_template_catalog(client, admin_user):
    client.force_login(admin_user)

    response = client.get("/verwaltung/themes/", secure=True)

    assert response.status_code == 200
    assert b"CSS-Vorlagen vergleichen" not in response.content
    assert b"Tailwind-Vorlagen vergleichen" not in response.content
    assert b"/verwaltung/themes/vorschau/" not in response.content


@pytest.mark.django_db
def test_every_portal_theme_uses_the_same_preview_without_becoming_active(client, guardian):
    theme = PortalTheme.objects.create(
        key="future-theme",
        name="Future Theme",
        description="Automatisch in der gemeinsamen Vorschau",
        audience=PortalTheme.Audience.ADULTS,
        primary="#123456",
        primary_dark="#102030",
        primary_light="#EAF0F4",
        accent="#ABCDEF",
        background="#F8FAFC",
        surface="#FFFFFF",
        text="#172033",
        text_muted="#667085",
    )
    client.force_login(guardian)

    overview = client.get(
        f"/einstellungen/design/vorschau/{theme.id}/uebersicht/", secure=True
    )
    calendar = client.get(
        f"/einstellungen/design/vorschau/{theme.id}/kalender/", secure=True
    )
    guardian.refresh_from_db()

    assert overview.status_code == 200
    assert calendar.status_code == 200
    assert b"template-portal-theme" in overview.content
    assert b"--color-primary:#123456" in overview.content
    assert b"Future Theme" in overview.content
    assert b"Klassenrat" in calendar.content
    assert guardian.selected_theme_id is None


@pytest.mark.django_db
def test_theme_settings_links_to_preview_instead_of_activating_it(client, guardian):
    theme = PortalTheme.objects.create(
        key="preview-link",
        name="Preview Link",
        audience=PortalTheme.Audience.ADULTS,
    )
    client.force_login(guardian)

    response = client.get("/einstellungen/profil/?tab=themes", secure=True)

    assert response.status_code == 200
    assert f"/einstellungen/design/vorschau/{theme.id}/uebersicht/".encode() in response.content


@pytest.mark.django_db
def test_removed_template_preview_route_returns_404(client, admin_user):
    client.force_login(admin_user)

    assert (
        client.get("/verwaltung/themes/vorschau/velora-ui/uebersicht/", secure=True).status_code
        == 404
    )
