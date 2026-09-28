import pytest

from klasse5e.core.models import PortalTheme


@pytest.mark.django_db
@pytest.mark.parametrize("audience,active", [("children", True), ("adults", False)])
def test_unavailable_theme_cannot_be_previewed_or_applied(client, guardian, audience, active):
    theme = PortalTheme.objects.create(
        key="unavailable", name="Unavailable", audience=audience, is_active=active
    )
    client.force_login(guardian)
    previous = guardian.selected_theme_id
    listing = client.get("/einstellungen/profil/?tab=themes")
    assert theme not in listing.context["themes"]
    assert client.get(
        f"/einstellungen/design/vorschau/{theme.pk}/uebersicht/"
    ).status_code == 404
    assert client.post("/einstellungen/profil/", {
        "save_scope": "themes", "theme_id": theme.pk,
    }).status_code == 404
    guardian.refresh_from_db()
    assert guardian.selected_theme_id == previous


@pytest.mark.django_db
def test_available_theme_only_persists_on_explicit_apply(client, guardian):
    theme = PortalTheme.objects.create(key="apply-theme", name="Apply Theme", audience="all")
    client.force_login(guardian)
    previous = guardian.selected_theme_id
    assert client.get(f"/einstellungen/design/vorschau/{theme.pk}/uebersicht/").status_code == 200
    guardian.refresh_from_db()
    assert guardian.selected_theme_id == previous
    assert client.post("/einstellungen/profil/", {
        "save_scope": "themes", "theme_id": theme.pk,
    }).status_code == 302
    guardian.refresh_from_db()
    assert guardian.selected_theme_id == theme.pk


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
def test_theme_management_can_update_tokens_without_auto_activating(client, admin_user):
    theme = PortalTheme.objects.create(
        key="editable-theme",
        name="Editable Theme",
        audience=PortalTheme.Audience.ADULTS,
        is_active=False,
        primary="#123456",
    )
    client.force_login(admin_user)

    response = client.post(
        "/verwaltung/themes/",
        {
            "action": "update",
            "theme_id": theme.id,
            "name": "Updated Theme",
            "description": "Updated description",
            "audience": "all",
            "primary": "#ABCDEF",
            "primary_dark": "#102030",
            "primary_light": "#EAF0F4",
            "accent": "#FEDCBA",
            "background": "#F8FAFC",
            "surface": "#FFFFFF",
            "text": "#172033",
            "text_muted": "#667085",
            "radius": "1rem",
            "shadow_strength": "12",
        },
        secure=True,
    )

    theme.refresh_from_db()
    assert response.status_code == 302
    assert theme.name == "Updated Theme"
    assert theme.primary == "#ABCDEF"
    assert theme.shadow_strength == 12
    assert theme.is_active is False


@pytest.mark.django_db
def test_removed_template_preview_route_returns_404(client, admin_user):
    client.force_login(admin_user)

    assert (
        client.get("/verwaltung/themes/vorschau/velora-ui/uebersicht/", secure=True).status_code
        == 404
    )


@pytest.mark.django_db
def test_invalid_theme_edit_preserves_input_and_database(client, admin_user):
    theme = PortalTheme.objects.create(key="invalid-edit", name="Original")
    client.force_login(admin_user)
    payload = {name: getattr(theme, name) for name in (
        "primary", "primary_dark", "primary_light", "accent", "background",
        "surface", "text", "text_muted", "radius", "shadow_strength", "audience",
    )}
    payload.update(action="update", theme_id=theme.pk, name="Unfertiger Entwurf", shadow_strength="100")
    response = client.post("/verwaltung/themes/", payload)
    assert response.status_code == 400
    assert response.context["theme_form"]["name"].value() == "Unfertiger Entwurf"
    assert "shadow_strength" in response.context["theme_form"].errors
    theme.refresh_from_db()
    assert theme.name == "Original"
    payload["shadow_strength"] = "10"
    assert client.post("/verwaltung/themes/", payload).status_code == 302
    theme.refresh_from_db()
    assert theme.name == "Unfertiger Entwurf"
