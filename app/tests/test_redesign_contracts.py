import pytest
from django.template.loader import get_template
from django.conf import settings

from klasse5e.core.avatar_designer import parse_avatar_seed, validate_avatar_seed
from klasse5e.core.models import PortalTheme, RoleAssignment
from klasse5e.core.templatetags.avatar_tags import avatar_composite


@pytest.mark.django_db
def test_design_system_has_own_editor_and_persists_valid_tokens(client, admin_user):
    client.force_login(admin_user)
    theme = PortalTheme.objects.first()
    page = client.get(f"/verwaltung/designsystem/?theme={theme.pk}")
    assert page.status_code == 200
    assert b'data-token-editor' in page.content
    assert b'data-token-specimen' in page.content
    payload = {key: getattr(theme, key) for key in (
        "primary", "primary_dark", "primary_light", "accent", "background", "surface", "text", "text_muted")}
    payload.update(theme_id=theme.pk, radius="1rem", shadow_strength="12", primary="#123456")
    response = client.post("/verwaltung/designsystem/", payload)
    assert response.status_code == 302
    theme.refresh_from_db()
    assert theme.primary == "#123456"
    assert theme.shadow_strength == 12
    admin_user.refresh_from_db()
    assert admin_user.selected_theme_id is None
    payload["primary"] = "red;display:none"
    response = client.post("/verwaltung/designsystem/", payload)
    assert response.status_code == 200
    assert b'errorlist' in response.content
    theme.refresh_from_db()
    assert theme.primary == "#123456"


@pytest.mark.django_db
def test_design_system_denies_non_admin(client, guardian):
    client.force_login(guardian)
    assert client.get("/verwaltung/designsystem/").status_code == 404
    assert client.post("/verwaltung/designsystem/", {}).status_code == 404


@pytest.mark.django_db
def test_person_detail_is_a_separate_work_surface(client, admin_user, guardian):
    client.force_login(admin_user)
    page = client.get(f"/verwaltung/rollen/personen/?user={guardian.pk}")
    assert page.status_code == 200
    assert b'person-role-card' in page.content
    assert b'id="people-table"' not in page.content
    assert 'Personenübersicht' in page.content.decode()
    assert client.get("/verwaltung/rollen/personen/?user=invalid").status_code == 404


@pytest.mark.django_db
def test_invalid_person_role_does_not_grant_or_crash(client, admin_user, guardian):
    client.force_login(admin_user)
    before = RoleAssignment.objects.filter(user=guardian, active=True).count()
    response = client.post("/verwaltung/rollen/personen/", {
        "user_id": guardian.pk, "action": "assign", "role": "primary_admin",
        "school_id": "broken",
    })
    assert response.status_code == 200
    assert b'role="alert"' in response.content
    assert RoleAssignment.objects.filter(user=guardian, active=True).count() == before


@pytest.mark.django_db
def test_admin_cannot_revoke_own_primary_role_via_person_card(client, admin_user):
    client.force_login(admin_user)
    role = RoleAssignment.objects.get(user=admin_user, role="primary_admin")
    response = client.post("/verwaltung/rollen/personen/", {
        "action": "revoke", "user_id": admin_user.pk, "assignment_id": role.pk,
    })
    assert response.status_code == 200
    role.refresh_from_db()
    assert role.active


@pytest.mark.parametrize("pose", [0, 1])
def test_avatar_v3_uses_full_pose_assets(pose):
    seed = f"v3:0:{pose}:0:0:0:0:0"
    assert validate_avatar_seed(seed) == seed
    assert parse_avatar_seed(seed)["pose"] == pose
    svg = str(avatar_composite(seed))
    assert f'pose/{"standing" if pose == 0 else "sitting"}' in svg
    assert "body/Hoodie.svg" not in svg


def test_templates_compile():
    for template in (settings.BASE_DIR / "templates").rglob("*.html"):
        get_template(str(template.relative_to(settings.BASE_DIR / "templates")))
