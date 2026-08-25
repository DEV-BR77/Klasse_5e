from datetime import date, timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from klasse5e.content.models import Comment, Post, ProtectedDocument
from klasse5e.core.models import (
    ConsentDecision,
    ConsentTextVersion,
    ConsentType,
    GuardianChildRelationship,
    Person,
    StudentProfile,
)
from klasse5e.core.policies import consent_state, family_label
from klasse5e.events.models import ContributionCategory, ContributionItem, Event, Reservation


@pytest.mark.django_db
def test_guardian_content_event_and_withdrawal_flow(client, guardian, school_class, year, settings):
    settings.MEDIA_ROOT = settings.BASE_DIR / "app" / ".test-media"
    student_person = Person.objects.create(first_name="Kim", last_name="Synthetic")
    StudentProfile.objects.create(person=student_person)
    GuardianChildRelationship.objects.create(
        guardian_person=guardian.person,
        student_person=student_person,
        relationship_type="mother",
        is_legal_guardian=True,
        may_view_student_profile=True,
        may_manage_general_consents=True,
        status="verified",
        valid_from=date(2026, 8, 1),
        verified_by=guardian,
        verified_at=timezone.now(),
    )
    consent_type = ConsentType.objects.create(
        key="general-push-integration",
        label="Push",
        category="general",
        purpose="Test",
        recipients="Mitglieder",
    )
    text = ConsentTextVersion.objects.create(
        consent_type=consent_type,
        version="draft-1",
        text="Fachlicher Entwurf",
        effective_from=timezone.now(),
    )
    decision = ConsentDecision.objects.create(
        consent_type=consent_type,
        text_version=text,
        subject_person=student_person,
        deciding_person=guardian.person,
        decision="granted",
    )
    assert consent_state(consent_type, student_person) == "allowed"

    document = ProtectedDocument.objects.create(
        school_class=school_class,
        school_year=year,
        title="Ablauf",
        category="Event",
        document_date=date(2026, 8, 25),
        version="1",
        original=SimpleUploadedFile("plan.pdf", b"%PDF-1.7\nsynthetic\n%%EOF"),
        status="published",
        created_by=guardian,
    )
    post = Post.objects.create(
        school_class=school_class,
        school_year=year,
        title="Fest",
        body="Information",
        category="Event",
        author=guardian,
        status="published",
    )
    event = Event.objects.create(
        school_class=school_class,
        school_year=year,
        title="Fest",
        description="Synthetisch",
        starts_at=timezone.now() + timedelta(days=5),
        ends_at=timezone.now() + timedelta(days=5, hours=2),
        location="Testort",
        change_deadline=timezone.now() + timedelta(days=3),
        status="published",
        post=post,
    )
    event.organizers.add(guardian)
    category = ContributionCategory.objects.create(event=event, name="Obst")
    item = ContributionItem.objects.create(
        category=category, label="Äpfel", desired_quantity=1, unit="Korb"
    )

    client.force_login(guardian)
    assert client.get(f"/documents/{document.id}/original/").status_code == 200
    assert client.post(f"/posts/{post.id}/comments/", {"body": "Wir kommen"}).status_code == 201
    assert (
        client.post(
            f"/items/{item.id}/reserve/", {"quantity": "1"}, HTTP_IDEMPOTENCY_KEY="integration-1"
        ).status_code
        == 201
    )
    assert Comment.objects.get().author == guardian
    assert Reservation.objects.get().user == guardian
    assert family_label(guardian) == "Alex · Mutter von Kim"

    decision.revoked_at = timezone.now()
    decision.save(update_fields=["revoked_at"])
    assert consent_state(consent_type, student_person) == "not_allowed"
