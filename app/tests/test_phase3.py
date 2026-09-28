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
    PortalModule,
    RelationshipStatus,
    RoleAssignment,
    RoleModulePermission,
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


@pytest.mark.django_db
def test_document_role_grant_can_be_revoked(client, admin_user, document):
    client.force_login(admin_user)
    url = f"/documents/{document.id}/original/"
    response = client.get(url)
    assert response.status_code == 200
    RoleModulePermission.objects.filter(
        role="primary_admin", module=PortalModule.objects.get(key="pdf_forms"), action="read",
    ).update(active=False)
    assert client.get(url).status_code == 404


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
def test_teacher_directory_respects_contact_visibility(client, guardian, school_class):
    person = Person.objects.create(first_name="Tessa", last_name="Synthetic")
    TeacherProfile.objects.create(
        person=person, school_class=school_class, subjects="Mathematik",
        class_function="Klassenleitung", school_email="tessa@example.test",
        office_hours="Dienstag nach Vereinbarung", email_visibility=Visibility.MEMBERS,
        office_hours_visibility=Visibility.HIDDEN,
    )
    client.force_login(guardian)

    page = client.get("/mehr/lehrkraefte/", secure=True)

    content = page.content.decode()
    assert page.status_code == 200
    assert "Klassenleitung" in content
    assert "Mathematik" in content
    assert 'href="mailto:tessa@example.test"' in content
    assert "Dienstag nach Vereinbarung" not in content


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
def test_post_detail_comment_form_returns_to_the_post(client, guardian, school_class, year):
    post = Post.objects.create(
        school_class=school_class, school_year=year, title="Info", body="Text",
        category="Allgemein", author=guardian, status="published",
    )
    client.force_login(guardian)
    page = client.get(f"/mehr/aktuelles/{post.id}/", secure=True)
    assert 'action="/posts/' in page.content.decode()
    response = client.post(
        f"/posts/{post.id}/comments/",
        {"body": "Ein Kommentar", "return_to": "post_detail"}, secure=True,
    )
    assert response.status_code == 302
    assert response.url == f"/mehr/aktuelles/{post.id}/"
    assert Comment.objects.get(post=post).body == "Ein Kommentar"


@pytest.mark.django_db
def test_family_label_only_from_verified_relation(guardian):
    student = Person.objects.create(first_name="Mia", last_name="Synthetic")
    GuardianChildRelationship.objects.create(
        guardian_person=guardian.person,
        student_person=student,
        relationship_type="guardian",
        status=RelationshipStatus.VERIFIED,
        verified_at=timezone.now(),
        valid_from=date(2026, 1, 1),
    )
    assert family_label(guardian) == "Alex · Erziehungsberechtigte Person von Mia"


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


@pytest.mark.django_db
def test_post_detail_never_renders_text_of_hidden_or_withdrawn_comments(
    client, guardian, school_class, year
):
    post = Post.objects.create(
        school_class=school_class, school_year=year, title="Info", body="Text",
        category="A", author=guardian, status="published",
    )
    Comment.objects.create(
        post=post, author=guardian, body="Geheimer moderierter Text", status=Comment.Status.HIDDEN
    )
    Comment.objects.create(
        post=post, author=guardian, body="Geheimer zurückgezogener Text", status=Comment.Status.WITHDRAWN
    )
    client.force_login(guardian)

    page = client.get(f"/mehr/aktuelles/{post.id}/", secure=True)

    assert page.status_code == 200
    content = page.content.decode()
    assert "Geheimer moderierter Text" not in content
    assert "Geheimer zurückgezogener Text" not in content
    assert "Dieser Kommentar ist nicht sichtbar." in content
    assert "Dieser Kommentar wurde zurückgezogen." in content
