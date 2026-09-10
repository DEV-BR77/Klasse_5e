import json
from unittest.mock import patch

import pytest
from cryptography.fernet import Fernet
from django.utils import timezone

from klasse5e.core.models import ClassMembership, GuardianChildRelationship, Person
from klasse5e.portal_adapters.models import ChildModuleConnection, PortalAdapter, PortalAdapterModule
from klasse5e.webuntis.client import ALLOWED_HOST, EndpointUnsupported, WebUntisClient
from klasse5e.webuntis.crypto import decrypt, encrypt
from klasse5e.webuntis.services import configured_endpoint


def test_https_and_fixed_host():
    client = WebUntisClient("user", "password")
    assert client.base.startswith("https://thgwob.webuntis.com/")
    assert ALLOWED_HOST == "thgwob.webuntis.com"
    with pytest.raises(ValueError):
        WebUntisClient("u", "p", server="evil.example")


def test_second_allowlisted_school_host_is_supported():
    client = WebUntisClient("user", "password", server="heinrich-nordhoff.webuntis.com")
    assert client.base.startswith("https://heinrich-nordhoff.webuntis.com/")


@pytest.mark.django_db
def test_school_adapter_endpoint_is_resolved_per_child(guardian, school_class):
    student = Person.objects.create(first_name="School", last_name="Child")
    ClassMembership.objects.create(
        person=student, school_class=school_class, valid_from=timezone.localdate()
    )
    GuardianChildRelationship.objects.create(
        guardian_person=guardian.person,
        student_person=student,
        relationship_type="father",
        is_legal_guardian=True,
        may_view_student_profile=True,
        valid_from=timezone.localdate(),
        status="verified",
        verified_by=guardian,
        verified_at=timezone.now(),
    )
    adapter = PortalAdapter.objects.create(
        school=school_class.school,
        provider=PortalAdapter.Provider.WEBUNTIS,
        name="Nordhoff WebUntis",
        base_url="https://heinrich-nordhoff.webuntis.com/WebUntis/#/basic/login",
        is_enabled=True,
    )
    module = PortalAdapterModule.objects.create(
        adapter=adapter,
        key="timetable",
        label="Stundenplan",
        is_enabled=True,
        requires_child_credentials=True,
    )
    ChildModuleConnection.objects.create(student=student, module=module, is_enabled=True)
    assert configured_endpoint(student) == ("heinrich-nordhoff.webuntis.com", "heinrich-nordhoff")


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


def test_json_rpc_posts_use_json_content_type():
    client = WebUntisClient("u", "p")

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return None

        def read(self):
            return json.dumps({"result": {}}).encode()

    with patch("urllib.request.urlopen", return_value=Response()) as urlopen:
        client._request("https://thgwob.webuntis.com/WebUntis/jsonrpc.do", {"id": 1})

    request = urlopen.call_args.args[0]
    assert request.get_header("Content-type") == "application/json"
