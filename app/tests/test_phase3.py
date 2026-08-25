from datetime import date

import pytest
from allauth.mfa.models import Authenticator
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from klasse5e.content.models import Comment, Post, ProtectedDocument, TeacherProfile, validate_pdf
from klasse5e.core.models import (
    AuditEvent,
    ClassMembership,
    GuardianChildRelationship,
    Person,
    RelationshipStatus,
    RoleAssignment,
    UserAccount,
    Visibility,
)
from klasse5e.core.policies import family_label


def pdf(name="document.pdf"):
    return SimpleUploadedFile(name, b"%PDF-1.7\nsynthetic\n%%EOF", content_type="application/pdf")


@pytest.fixture
def document(db, guardian, school_class, year, settings):
    settings.MEDIA_ROOT = settings.BASE_DIR / "app" / ".test-media"
    return ProtectedDocument.objects.create(
        school_class=school_class,
        school_year=year,
        title="Synthetic PDF",
        category="Info",
        document_date=date(2026, 8, 25),
        version="1",
        original=pdf(),
        fillable=pdf("fillable.pdf"),
        status="published",
        created_by=guardian,
    )


@pytest.mark.django_db
def test_document_requires_login_and_class(client, document):
    assert client.get(f"/documents/{document.id}/original/").status_code == 302
    outsider = UserAccount.objects.create_user("outsider@example.test", "Pass-123456789!")
    Person.objects.create(user=outsider, first_name="Out", last_name="Synthetic")
    client.force_login(outsider)
    assert client.get(f"/documents/{document.id}/original/").status_code == 404


@pytest.mark.django_db
def test_authorized_original_and_fillable_download_audited(client, guardian, document):
    client.force_login(guardian)
    for variant in ["original", "fillable"]:
        response = client.get(f"/documents/{document.id}/{variant}/")
        assert response.status_code == 200 and response["Content-Type"] == "application/pdf"
    assert AuditEvent.objects.filter(action="document.download").count() == 2


def test_pdf_content_is_validated():
    with pytest.raises(ValidationError):
        validate_pdf(SimpleUploadedFile("fake.pdf", b"not-a-pdf"))


@pytest.mark.django_db
def test_editor_role_does_not_grant_account_admin(guardian, school_class):
    RoleAssignment.objects.create(user=guardian, school_class=school_class, role="editor")
    assert not guardian.is_staff and not guardian.is_superuser


@pytest.mark.django_db
def test_teacher_fields_default_hidden(school_class):
    person = Person.objects.create(first_name="Tessa", last_name="Synthetic")
    profile = TeacherProfile.objects.create(
        person=person,
        school_class=school_class,
        subjects="Mathematik",
        class_function="Klassenleitung",
    )
    assert profile.email_visibility == Visibility.HIDDEN


@pytest.mark.django_db
def test_comments_require_membership_and_open_topic(client, guardian, school_class, year):
    post = Post.objects.create(
        school_class=school_class,
        school_year=year,
        title="Info",
        body="Text",
        category="Allgemein",
        author=guardian,
        status="published",
    )
    client.force_login(guardian)
    assert client.post(f"/posts/{post.id}/comments/", {"body": "Hallo"}).status_code == 201
    assert Comment.objects.get().author == guardian
    post.comments_closed = True
    post.save()
    assert client.post(f"/posts/{post.id}/comments/", {"body": "Spät"}).status_code == 400


@pytest.mark.django_db
def test_family_label_only_from_verified_relation(guardian):
    student = Person.objects.create(first_name="Mia", last_name="Synthetic")
    GuardianChildRelationship.objects.create(
        guardian_person=guardian.person,
        student_person=student,
        relationship_type="father",
        status=RelationshipStatus.VERIFIED,
        verified_at=timezone.now(),
        valid_from=date(2026, 1, 1),
    )
    assert family_label(guardian) == "Alex · Vater von Mia"


@pytest.mark.django_db
def test_withdraw_and_moderation(client, guardian, school_class, year):
    moderator = UserAccount.objects.create_user("moderator@example.test", "Pass-123456789!")
    mp = Person.objects.create(user=moderator, first_name="Mod", last_name="Synthetic")
    ClassMembership.objects.create(
        school_class=school_class, person=mp, valid_from=date(2026, 8, 1)
    )
    RoleAssignment.objects.create(user=moderator, school_class=school_class, role="moderator")
    Authenticator.objects.create(
        user=moderator,
        type=Authenticator.Type.TOTP,
        data={"secret": "synthetic-test-only"},
    )
    post = Post.objects.create(
        school_class=school_class,
        school_year=year,
        title="Info",
        body="Text",
        category="A",
        author=guardian,
        status="published",
    )
    comment = Comment.objects.create(post=post, author=guardian, body="Text")
    client.force_login(guardian)
    assert client.post(f"/comments/{comment.id}/withdraw/").status_code == 204
    comment.status = "visible"
    comment.save()
    client.force_login(moderator)
    assert client.post(f"/comments/{comment.id}/moderate/").status_code == 204
    assert AuditEvent.objects.filter(action="comment.moderated").exists()
