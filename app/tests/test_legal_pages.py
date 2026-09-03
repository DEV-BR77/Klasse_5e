import pytest


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def legal_page_settings(settings):
    settings.SECURE_SSL_REDIRECT = False


def test_imprint_contains_complete_operator_details(client):
    response = client.get("/impressum/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "Björn Radke" in html
    assert "Weißdornweg 4" in html
    assert "38440 Wolfsburg" in html
    assert "kontakt@klassid.de" in html
    assert "Elternvertretung der Klasse 5e" not in html
    assert 'href="/open-source-lizenzen/"' in html


def test_shared_footer_groups_copyright_and_legal_links(client):
    response = client.get("/impressum/")

    html = response.content.decode()
    assert 'class="site-footer"' in html
    assert "© 2026 KlassID" in html
    assert "Privat betrieben" in html
    assert 'href="/datenschutz/"' in html
    assert 'href="/impressum/"' in html
    assert 'href="/nutzung/"' in html


def test_open_source_page_lists_the_main_runtime_components(client):
    response = client.get("/open-source-lizenzen/")

    assert response.status_code == 200
    html = response.content.decode()
    assert "Django" in html
    assert "Wagtail" in html
    assert "BSD-3-Clause" in html
    assert "pywebpush" in html
    assert "MPL-2.0" in html
    assert "OpenCV Python" in html
    assert "Apache-2.0" in html
