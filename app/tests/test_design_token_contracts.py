import pytest

from klasse5e.core.models import PortalTheme


def _payload(theme, **overrides):
    names = (
        "primary", "primary_dark", "primary_light", "accent", "background", "surface",
        "text", "text_muted", "border", "success", "warning", "danger", "typography",
        "density", "radius", "shadow_strength",
    )
    payload = {name: getattr(theme, name) for name in names}
    payload.update(theme_id=theme.pk, **overrides)
    return payload


@pytest.mark.django_db
def test_design_system_persists_and_emits_all_semantic_tokens(client, admin_user):
    theme = PortalTheme.objects.create(key="semantic-token-test", name="Semantic Token Test")
    client.force_login(admin_user)

    response = client.post(
        "/verwaltung/designsystem/",
        _payload(
            theme,
            border="#CBD5E1",
            success="#067647",
            warning="#934B00",
            danger="#B42318",
            typography="rounded",
            density="compact",
        ),
    )

    assert response.status_code == 302
    theme.refresh_from_db()
    assert theme.typography == "rounded"
    assert theme.density == "compact"
    assert "--color-border:#CBD5E1" in theme.css_variables
    assert "--color-success:#067647" in theme.css_variables
    assert "--color-warning:#934B00" in theme.css_variables
    assert "--color-error:#B42318" in theme.css_variables
    assert "--font-body:" in theme.css_variables
    assert "--control-height-md:2.5rem" in theme.css_variables
    assert "--theme-panel-padding:1rem" in theme.css_variables


@pytest.mark.django_db
def test_design_system_rejects_unreadable_text_and_status_tokens(client, admin_user):
    theme = PortalTheme.objects.create(key="contrast-test", name="Contrast Test")
    client.force_login(admin_user)

    response = client.post(
        "/verwaltung/designsystem/",
        _payload(theme, text="#F8FAFC", success="#F8FAFC"),
    )

    assert response.status_code == 200
    assert "mindestens 4,5:1" in response.content.decode()
    assert "mindestens 3:1" in response.content.decode()
    theme.refresh_from_db()
    assert theme.text == "#25283A"
    assert theme.success == "#087A4B"


@pytest.mark.django_db
def test_design_system_page_groups_tokens_and_keeps_preview_non_persistent(client, admin_user):
    theme = PortalTheme.objects.create(key="editor-layout-test", name="Editor Layout Test")
    client.force_login(admin_user)

    response = client.get(f"/verwaltung/designsystem/?theme={theme.pk}")
    body = response.content.decode()

    assert response.status_code == 200
    assert "Marke und Flächen" in body
    assert "Text, Linien und Zustände" in body
    assert "Typografie und Geometrie" in body
    assert 'data-token-specimen' in body
    assert "Design-Tokens speichern" in body
    admin_user.refresh_from_db()
    assert admin_user.selected_theme_id is None
