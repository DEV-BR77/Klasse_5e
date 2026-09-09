import pytest
from django.core.signing import TimestampSigner


@pytest.mark.django_db
def test_signed_scan_link_renders_the_authenticated_dashboard_without_redirect(client, guardian):
    token = TimestampSigner(salt="klassid-scan-access").sign(str(guardian.pk))

    response = client.get(f"/scan/{token}/")

    assert response.status_code == 200
    assert response.wsgi_request.user == guardian
    assert "Start" in response.content.decode()
    assert "no-store" in response["Cache-Control"]


@pytest.mark.django_db
def test_expired_or_invalid_scan_link_is_not_authenticated(client):
    response = client.get("/scan/not-a-valid-token/")

    assert response.status_code == 410


@pytest.mark.django_db
def test_scan_link_accepts_only_safe_get_requests(client, guardian):
    token = TimestampSigner(salt="klassid-scan-access").sign(str(guardian.pk))

    response = client.post(f"/scan/{token}/")

    assert response.status_code == 405
