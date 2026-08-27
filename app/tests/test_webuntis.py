import json
from unittest.mock import patch

import pytest
from cryptography.fernet import Fernet

from klasse5e.webuntis.client import ALLOWED_HOST, EndpointUnsupported, WebUntisClient
from klasse5e.webuntis.crypto import decrypt, encrypt


def test_https_and_fixed_host():
    client = WebUntisClient("user", "password")
    assert client.base.startswith("https://thgwob.webuntis.com/")
    assert ALLOWED_HOST == "thgwob.webuntis.com"
    with pytest.raises(ValueError):
        WebUntisClient("u", "p", server="evil.example")


def test_arbitrary_endpoint_is_rejected():
    client = WebUntisClient("u", "p")
    with pytest.raises(EndpointUnsupported):
        client.rpc("untis_raw_call")


@pytest.mark.django_db
def test_credentials_are_authenticated_encrypted(settings):
    settings.WEBUNTIS_CREDENTIAL_ENCRYPTION_KEY = Fernet.generate_key().decode()
    token = encrypt("synthetic-password")
    assert b"synthetic-password" not in token
    assert decrypt(token) == "synthetic-password"


def test_close_discards_ephemeral_tokens():
    client = WebUntisClient("u", "p")
    client._session_id = "synthetic-session"
    client._jwt = "synthetic-jwt"
    with patch.object(client, "_request"):
        client.close()
    assert client._session_id is None
    assert client._jwt is None
