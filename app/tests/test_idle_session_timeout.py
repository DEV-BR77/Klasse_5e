from unittest.mock import patch

import pytest

from klasse5e.core.models import AuditEvent, PortalConfigurationKey, PortalConfigurationValue
from klasse5e.core.session_security import idle_timeout_minutes


@pytest.mark.django_db
def test_default_idle_timeout_is_fifteen_minutes(client, guardian):
    key = PortalConfigurationKey.objects.get(key="session_idle_timeout_minutes")
    assert key.default_value == 15
    assert key.value_type == "integer"
    assert idle_timeout_minutes() == 15

    client.force_login(guardian)
    response = client.get("/")
    assert response.status_code == 200
    assert b'data-idle-session-timeout="900"' in response.content


@pytest.mark.django_db
def test_portal_admin_can_update_idle_timeout_and_audit(client, admin_user):
    client.force_login(admin_user)
    response = client.post(
        "/verwaltung/automatische-abmeldung/", {"idle_timeout_minutes": "7"}, secure=True
    )
    assert response.status_code == 302
    assert idle_timeout_minutes() == 7
    assert (
        PortalConfigurationValue.objects.get(
            key__key="session_idle_timeout_minutes", school__isnull=True, school_class__isnull=True
        ).value
        == 7
    )
    assert AuditEvent.objects.filter(
        actor=admin_user, action="session.idle_timeout.changed", metadata__minutes=7
    ).exists()


@pytest.mark.django_db
def test_guardian_cannot_read_or_change_idle_timeout(client, guardian):
    client.force_login(guardian)
    assert client.get("/verwaltung/automatische-abmeldung/", secure=True).status_code == 404
    assert (
        client.post(
            "/verwaltung/automatische-abmeldung/", {"idle_timeout_minutes": "7"}, secure=True
        ).status_code
        == 404
    )
    assert idle_timeout_minutes() == 15


@pytest.mark.django_db
@pytest.mark.parametrize("value", ["", "0", "121", "1.5", "true"])
def test_timeout_configuration_rejects_invalid_bounds(client, admin_user, value):
    client.force_login(admin_user)
    response = client.post(
        "/verwaltung/automatische-abmeldung/", {"idle_timeout_minutes": value}, secure=True
    )
    assert response.status_code == 302
    assert not PortalConfigurationValue.objects.filter(
        key__key="session_idle_timeout_minutes"
    ).exists()


@pytest.mark.django_db
def test_server_ends_idle_session_on_the_next_request(client, guardian):
    client.force_login(guardian)
    session = client.session
    session["idle_session_last_activity"] = 1_000
    session.save()

    with patch("klasse5e.core.middleware.time", return_value=1_900):
        response = client.get("/", secure=True)

    assert response.status_code == 302
    assert response.url == "/accounts/login/?timeout=1"
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
def test_background_poll_does_not_keep_an_idle_session_alive(client, guardian):
    client.force_login(guardian)
    session = client.session
    session["idle_session_last_activity"] = 1_000
    session.save()

    with patch("klasse5e.core.middleware.time", return_value=1_900):
        response = client.get("/chat/", HTTP_X_KLASSID_BACKGROUND_POLL="1", secure=True)

    assert response.status_code == 302
    assert response.url == "/accounts/login/?timeout=1"


@pytest.mark.django_db
def test_browser_timeout_endpoint_is_csrf_protected_and_logs_out(client, guardian):
    from django.test import Client

    csrf_client = Client(enforce_csrf_checks=True)
    csrf_client.force_login(guardian)
    assert csrf_client.post("/sessions/idle-timeout/", secure=True).status_code == 403

    client.force_login(guardian)
    assert client.post("/sessions/idle-timeout/", secure=True).status_code == 204
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
def test_mfa_setup_page_is_also_covered_by_the_idle_timeout(client, admin_user):
    client.force_login(admin_user)
    session = client.session
    session["idle_session_last_activity"] = 1_000
    session.save()

    with patch("klasse5e.core.middleware.time", return_value=1_900):
        response = client.get("/accounts/2fa/totp/activate/", secure=True)

    assert response.status_code == 302
    assert response.url == "/accounts/login/?timeout=1"
