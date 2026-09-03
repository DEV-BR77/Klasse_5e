import pytest


pytestmark = pytest.mark.django_db


def test_invitation_entry_is_public_and_explains_code_flow(client):
    response = client.get("/einladung/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "Einladungscode eingeben" in html
    assert "Code prüfen" in html
    assert "Zur Anmeldung" in html


def test_project_and_demo_pages_are_public(client):
    project = client.get("/projekt/")
    demo = client.get("/demo/")

    assert project.status_code == 200
    assert "Der Treffpunkt für Schule und Familie" in project.content.decode()
    assert demo.status_code == 200
    demo_html = demo.content.decode()
    assert "nur Beispiele" in demo_html
    assert "Bild geschützt" in demo_html
    assert "keine echten Namen" in demo_html
