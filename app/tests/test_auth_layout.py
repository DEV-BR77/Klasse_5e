import pytest


@pytest.mark.django_db
def test_login_uses_branded_invitation_layout(client):
    response = client.get("/accounts/login/")
    content = response.content.decode()

    assert response.status_code == 200
    assert 'class="auth-page"' in content
    assert "/static/css/dist/styles.css" in content
    assert "/static/auth.css" not in content
    assert 'branding/klassid-main.png' not in content
    assert 'class="sr-only">Bei KlassID anmelden</h1>' in content
    assert "KlassID</p>" in content
    assert "Deine Klasse - alles im Blick." in content
    assert "Hausaufgaben, Stundenplan, Speiseplan, Mitteilungen, Abwesenheiten." in content
    assert "Klar, geschützt, alles an einem Ort." in content
    assert "DSGVO-konform und lokal" in content
    assert "Keine Cookies, keine Werbe-Tracker" in content
    assert "Du entscheidest, was angezeigt wird." in content
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


@pytest.mark.django_db
def test_login_timeout_notice_is_centered_and_dismissible(client):
    response = client.get("/accounts/login/?timeout=1")
    content = response.content.decode()

    assert response.status_code == 200
    assert 'class="status-banner"' in content
    assert 'data-timeout-notice' in content
    assert 'data-timeout-notice-close' in content
    assert "Verstanden" in content
