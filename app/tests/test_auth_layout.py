def test_login_uses_branded_closed_registration_layout(client):
    response = client.get("/accounts/login/")
    content = response.content.decode()

    assert response.status_code == 200
    assert 'class="auth-page"' in content
    assert "/static/auth." in content and ".css" in content
    assert "Keine öffentliche Registrierung" in content
    assert "/accounts/signup/" not in content
