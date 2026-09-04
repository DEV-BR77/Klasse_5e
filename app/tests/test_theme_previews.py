import pytest

from klasse5e.core.models import PortalTheme
from klasse5e.core.ui_views import TEMPLATE_PREVIEW_CATALOG


@pytest.mark.django_db
def test_template_catalog_offers_shared_dashboard_and_calendar_previews(client, admin_user):
    client.force_login(admin_user)

    management = client.get("/verwaltung/themes/", secure=True)

    assert management.status_code == 200
    assert management.content.count(b">Vorschau</a>") >= len(TEMPLATE_PREVIEW_CATALOG)
    for item in TEMPLATE_PREVIEW_CATALOG:
        overview = client.get(
            f"/verwaltung/themes/vorschau/{item['key']}/uebersicht/", secure=True
        )
        calendar = client.get(
            f"/verwaltung/themes/vorschau/{item['key']}/kalender/", secure=True
        )
        assert overview.status_code == 200
        assert calendar.status_code == 200
        assert item["name"].encode() in overview.content
        assert b"Was steht heute an?" in overview.content
        assert b"07.\xe2\x80\x9313. September 2026" in calendar.content
        assert b"Sportfest" in calendar.content


@pytest.mark.django_db
def test_catalog_preview_is_hidden_from_guardians(client, guardian):
    client.force_login(guardian)

    response = client.get(
        "/verwaltung/themes/vorschau/velora-ui/uebersicht/", secure=True
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_every_portal_theme_uses_the_same_previews_without_becoming_active(client, guardian):
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

    response = client.get("/einstellungen/design/", secure=True)

    assert response.status_code == 200
    assert f"/einstellungen/design/vorschau/{theme.id}/uebersicht/".encode() in response.content


@pytest.mark.django_db
def test_unknown_preview_page_or_template_returns_404(client, admin_user):
    client.force_login(admin_user)

    assert (
        client.get(
            "/verwaltung/themes/vorschau/does-not-exist/uebersicht/", secure=True
        ).status_code
        == 404
    )
    assert (
        client.get(
            "/verwaltung/themes/vorschau/velora-ui/unbekannt/", secure=True
        ).status_code
        == 404
    )
