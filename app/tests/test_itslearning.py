import base64
from datetime import date, timedelta

import pytest
from cryptography.fernet import Fernet
from django.test import override_settings
from django.utils import timezone

from klasse5e.core.models import (
    ClassMembership,
    GuardianChildRelationship,
    MembershipStatus,
    Person,
    RelationshipStatus,
    School,
    SchoolClass,
    SchoolYear,
    StudentProfile,
    UserAccount,
)
from klasse5e.itslearning.models import ItslearningConnection, WebDavSpace


@pytest.fixture
def family(db):
    user = UserAccount.objects.create_user(
        email="guardian@example.test", password="synthetic-login-password"
    )
    guardian = Person.objects.create(user=user, first_name="Test", last_name="Guardian")
    child = Person.objects.create(first_name="Test", last_name="Student")
    student = StudentProfile.objects.create(person=child)
    year = SchoolYear.objects.create(
        label="2099/2100",
        starts_on=date.today() - timedelta(days=30),
        ends_on=date.today() + timedelta(days=300),
        is_active=True,
    )
    school = School.objects.create(name="Testschule", slug="its-testschule")
    school_class = SchoolClass.objects.create(
        school=school, name="5e", code="5e", school_year=year
    )
    ClassMembership.objects.create(
        school_class=school_class,
        person=guardian,
        status=MembershipStatus.ACTIVE,
        valid_from=date.today() - timedelta(days=1),
    )
    GuardianChildRelationship.objects.create(
        guardian_person=guardian,
        student_person=child,
        relationship_type="guardian",
        status=RelationshipStatus.VERIFIED,
        verified_at=timezone.now(),
        valid_from=date.today() - timedelta(days=1),
        may_manage_profile=True,
    )
    return user, student


@pytest.mark.django_db
@override_settings(ITSLEARNING_CREDENTIAL_ENCRYPTION_KEY=Fernet.generate_key().decode())
def test_connection_secrets_are_encrypted(family):
    user, student = family
    connection = ItslearningConnection(owner=user, student=student)
    connection.set_secrets(
        "test-user",
        "synthetic-secret-value",
        "https://wob.itslearning.com/calendar/example.ics",
    )
    connection.save()
    assert b"test-user" not in bytes(connection.username_ciphertext)
    assert b"synthetic-secret-value" not in bytes(connection.password_ciphertext)


@pytest.mark.django_db
@override_settings(WEBDAV_ROOT=None)
def test_webdav_requires_basic_auth(client, family, settings, tmp_path):
    settings.WEBDAV_ROOT = tmp_path
    _, student = family
    space = WebDavSpace.objects.create(
        student=student, username="test-webdav", password_hash=""
    )
    space.set_password("synthetic-webdav-password")
    space.save()
    url = f"/dav/{space.public_id}/"
    assert client.generic("PROPFIND", url, secure=True).status_code == 401
    auth = base64.b64encode(b"test-webdav:synthetic-webdav-password").decode()
    response = client.generic(
        "PROPFIND",
        url,
        secure=True,
        HTTP_AUTHORIZATION=f"Basic {auth}",
        HTTP_DEPTH="1",
    )
    assert response.status_code == 207


@pytest.mark.django_db
@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
def test_guardian_can_open_portal(client, family):
    user, _ = family
    client.force_login(user)
    response = client.get("/itslearning/", secure=True)
    assert response.status_code == 200
    assert "itslearning" in response.content.decode().lower()
