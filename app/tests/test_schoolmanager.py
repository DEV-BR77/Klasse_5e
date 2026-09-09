from datetime import date

import pytest
from cryptography.fernet import Fernet
from django.test import override_settings

from klasse5e.core.models import ClassMembership, Person, UserNotification
from klasse5e.portal_adapters.catalog import seed_default_modules
from klasse5e.portal_adapters.models import PortalAdapter, SchoolmanagerConnection
from klasse5e.schoolmanager.browser import PlaywrightSchoolmanagerClient, SchoolmanagerItem
from klasse5e.schoolmanager.crypto import decrypt, encrypt
from klasse5e.schoolmanager.sync import sync_connection


@pytest.mark.django_db
@override_settings(WEBUNTIS_CREDENTIAL_ENCRYPTION_KEY=Fernet.generate_key().decode())
def test_schoolmanager_catalog_and_credentials_are_encrypted(admin_user, school, school_class):
    adapter = PortalAdapter.objects.create(
        school=school, provider=PortalAdapter.Provider.SCHULMANAGER,
        name="Schulmanager Online", is_enabled=True, requires_child_credentials=True,
    )
    seed_default_modules(adapter)
    assert set(adapter.modules.values_list("key", flat=True)) == {"messages", "letters"}
    child = Person.objects.create(first_name="Mila", last_name="Test")
    ClassMembership.objects.create(person=child, school_class=school_class, valid_from=date(2026, 8, 1), status="active")
    connection = SchoolmanagerConnection.objects.create(
        user=admin_user, student=child, username_encrypted=encrypt("user"), password_encrypted=encrypt("secret")
    )
    assert connection.username_encrypted != b"user"
    assert decrypt(connection.password_encrypted) == "secret"


@pytest.mark.django_db
def test_schoolmanager_sync_is_idempotent(admin_user, school_class):
    child = Person.objects.create(first_name="Mila", last_name="Test")
    ClassMembership.objects.create(person=child, school_class=school_class, valid_from=date(2026, 8, 1), status="active")
    connection = SchoolmanagerConnection.objects.create(
        user=admin_user, student=child, username_encrypted=b"x", password_encrypted=b"y"
    )
    class FakeClient:
        def __init__(self, *_args): pass
        def fetch(self):
            return [SchoolmanagerItem("messages", "42", "Elternabend")]
    with override_settings(WEBUNTIS_CREDENTIAL_ENCRYPTION_KEY=None):
        # Replace decryption at the call boundary to keep this test synthetic.
        from klasse5e.schoolmanager import sync
        original = sync.decrypt
        sync.decrypt = lambda value: "synthetic"
        try:
            assert sync_connection(connection, client_factory=FakeClient) == 1
            assert sync_connection(connection, client_factory=FakeClient) == 0
        finally:
            sync.decrypt = original
    assert UserNotification.objects.count() == 1


def test_client_normalizes_timeout_range():
    assert PlaywrightSchoolmanagerClient("u", "p", timeout_ms=1).timeout_ms == 5000
    assert PlaywrightSchoolmanagerClient("u", "p", timeout_ms=99999).timeout_ms == 45000
