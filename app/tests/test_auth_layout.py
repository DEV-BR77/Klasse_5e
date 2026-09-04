import pytest


@pytest.mark.django_db
def test_login_uses_branded_invitation_layout(client):
    response = client.get("/accounts/login/")
    content = response.content.decode()

    assert response.status_code == 200
    assert 'class="auth-page"' in content
    assert "/static/auth." in content and ".css" in content
    assert "Termine und Stundenplan im Blick" in content
    assert "Speiseplan und Mitbringlisten gemeinsam planen" in content
    assert "Du hast einen Einladungscode erhalten?" in content
    assert "/einladung/" in content
    assert "auth-project-card" in content
    assert "Projekt kennenlernen" in content
    assert "Demo ansehen" not in content
    assert "Mehr erfahren" not in content
    assert "Passkey" not in content
    assert "Sicherheitsschlüssel" not in content
    assert "Willkommen zurück" not in content
    assert "Melde dich mit deinem bestätigten KlassID-Konto an" not in content
    assert "/accounts/signup/" not in content
