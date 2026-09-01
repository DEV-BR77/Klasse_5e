import uuid
from datetime import timedelta

import pytest
from django.test import override_settings
from django.utils import timezone

from klasse5e.biometrics.models import (
    BiometricMatch,
    VisionPhotoSubmission,
)
from klasse5e.biometrics.policies import biometric_consent, may_search_profile
from klasse5e.biometrics.services import decide_match, enable_profile, withdraw_profile
from klasse5e.core.models import (
    ClassMembership,
    ConsentDecision,
    ConsentTextVersion,
    ConsentType,
    GuardianChildRelationship,
    Person,
    Role,
    RoleAssignment,
    School,
    SchoolClass,
    SchoolYear,
    StudentProfile,
    UserAccount,
)


class FakeVision:
    def __init__(self):
        self.calls = []

    def create_collection(self, cid, pipeline):
        self.calls.append(("collection", cid))
        return {"model_version": "det+rec"}

    def create_subject(self, cid, sid):
        self.calls.append(("subject", cid, sid))
        return {}

    def delete_subject(self, cid, sid):
        self.calls.append(("delete_subject", cid, sid))
        return {}

    def confirm(self, cid, mid, aid, add=False):
        self.calls.append(("confirm", cid, mid, add))
        return {}

    def reject(self, cid, mid, aid):
        self.calls.append(("reject", cid, mid))
        return {}

    def list_faces(self, cid, iid):
        return []

    def list_matches(self, cid, fid):
        return []

    def create_reference(self, cid, sid, rid, fid):
        self.calls.append(("reference", cid, sid, rid, fid))
        return {}

    def delete_reference(self, cid, sid, rid):
        self.calls.append(("delete_reference", cid, sid, rid))
        return {}


class FailingDeleteVision(FakeVision):
    def delete_subject(self, cid, sid):
        raise RuntimeError("synthetic_failure")


@pytest.fixture
def domain(db):
    today = timezone.localdate()
    year = SchoolYear.objects.create(
        label="Test", starts_on=today - timedelta(days=1), ends_on=today + timedelta(days=100)
    )
    school = School.objects.create(name="Testschule", slug="biometric-testschule")
    school_class = SchoolClass.objects.create(
        school=school, name="Synthetic", code="synthetic", school_year=year
    )
    admin = UserAccount.objects.create_user(email="ada@example.test", password="x")
    admin_person = Person.objects.create(user=admin, first_name="Ada", last_name="Admin")
    ClassMembership.objects.create(school_class=school_class, person=admin_person, valid_from=today)
    RoleAssignment.objects.create(user=admin, school_class=school_class, role=Role.MODERATOR)
    student_person = Person.objects.create(first_name="Sam", last_name="Synthetic")
    student = StudentProfile.objects.create(person=student_person)
    ClassMembership.objects.create(
        school_class=school_class, person=student_person, valid_from=today
    )
    guardian = UserAccount.objects.create_user(email="gina@example.test", password="x")
    guardian_person = Person.objects.create(user=guardian, first_name="Gina", last_name="Guardian")
    ClassMembership.objects.create(
        school_class=school_class, person=guardian_person, valid_from=today
    )
    RoleAssignment.objects.create(user=guardian, school_class=school_class, role=Role.GUARDIAN)
    GuardianChildRelationship.objects.create(
        guardian_person=guardian_person,
        student_person=student_person,
        relationship_type="guardian",
        is_legal_guardian=True,
        may_view_student_profile=True,
        may_manage_biometric_consents=True,
        valid_from=today,
        status="verified",
        verified_by=admin,
        verified_at=timezone.now(),
    )
    consent_type = ConsentType.objects.create(
        key="biometric-search",
        label="Biometrie",
        category="biometric",
        purpose="Test",
        recipients="lokaler Dienst",
    )
    version = ConsentTextVersion.objects.create(
        consent_type=consent_type, version="v1", text="Entwurf", effective_from=timezone.now()
    )
    ConsentDecision.objects.create(
        consent_type=consent_type,
        text_version=version,
        subject_person=student_person,
        deciding_person=guardian_person,
        decision="granted",
    )
    return admin, guardian, student, school_class, consent_type, version


@pytest.mark.django_db
def test_feature_is_disabled_by_default(domain):
    admin, _, student, school_class, _, _ = domain
    with pytest.raises(PermissionError, match="disabled"):
        enable_profile(student, school_class, actor=admin, client=FakeVision())


@pytest.mark.django_db
@override_settings(BIOMETRIC_SEARCH_ENABLED=True)
def test_profile_requires_every_current_guardian_consent(domain):
    admin, _, student, school_class, consent_type, version = domain
    other = Person.objects.create(first_name="Other", last_name="Guardian")
    GuardianChildRelationship.objects.create(
        guardian_person=other,
        student_person=student.person,
        relationship_type="mother",
        is_legal_guardian=True,
        may_manage_biometric_consents=True,
        valid_from=timezone.localdate(),
        status="verified",
        verified_by=admin,
        verified_at=timezone.now(),
    )
    assert biometric_consent(student.person)[0] is False
    with pytest.raises(PermissionError):
        enable_profile(student, school_class, actor=admin, client=FakeVision())
    ConsentDecision.objects.create(
        consent_type=consent_type,
        text_version=version,
        subject_person=student.person,
        deciding_person=other,
        decision="granted",
    )
    profile = enable_profile(student, school_class, actor=admin, client=FakeVision())
    assert profile.status == "active" and profile.collection.model_version == "det+rec"


@pytest.mark.django_db
@override_settings(BIOMETRIC_SEARCH_ENABLED=True)
def test_parent_can_only_search_linked_child(domain):
    admin, guardian, student, school_class, _, _ = domain
    profile = enable_profile(student, school_class, actor=admin, client=FakeVision())
    assert may_search_profile(guardian, profile)
    stranger = UserAccount.objects.create_user(email="stranger@example.test", password="x")
    stranger_person = Person.objects.create(user=stranger, first_name="No", last_name="Link")
    ClassMembership.objects.create(
        school_class=school_class, person=stranger_person, valid_from=timezone.localdate()
    )
    assert not may_search_profile(stranger, profile)


@pytest.mark.django_db
@override_settings(BIOMETRIC_SEARCH_ENABLED=True)
def test_match_never_auto_confirms_and_decision_is_idempotent(domain):
    admin, _, student, school_class, _, _ = domain
    profile = enable_profile(student, school_class, actor=admin, client=FakeVision())
    from klasse5e.media.models import Gallery, Photo

    gallery = Gallery.objects.create(
        school_class=school_class,
        school_year=school_class.school_year,
        title="Synthetic",
        created_by=admin,
    )
    photo = Photo.objects.create(
        gallery=gallery,
        uploader=admin,
        original_name="x.jpg",
        display_file="x",
        thumbnail_file="t",
        content_type="image/jpeg",
        size=1,
        width=1,
        height=1,
        sha256="0" * 64,
        retention_until=timezone.now() + timedelta(days=1),
    )
    submission = VisionPhotoSubmission.objects.create(
        collection=profile.collection,
        photo=photo,
        pipeline_id=profile.collection.pipeline_id,
        model_version="det+rec",
        source_delete_due_at=timezone.now() + timedelta(hours=24),
    )
    match = BiometricMatch.objects.create(
        collection=profile.collection,
        submission=submission,
        profile=profile,
        vision_face_id="face1",
        vision_match_id="match1",
        score=0.61,
        rank=1,
        pipeline_id="yunet",
        model_version="det+rec",
    )
    assert match.status == "proposed"
    fake = FakeVision()
    decide_match(match, actor=admin, decision="confirmed", client=fake)
    assert match.status == "confirmed" and len(fake.calls) == 1
    decide_match(match, actor=admin, decision="confirmed", client=fake)
    assert len(fake.calls) == 1


@pytest.mark.django_db
@override_settings(BIOMETRIC_SEARCH_ENABLED=True)
def test_withdrawal_deletes_remote_subject_and_local_matches(domain):
    admin, _, student, school_class, _, _ = domain
    fake = FakeVision()
    profile = enable_profile(student, school_class, actor=admin, client=fake)
    withdraw_profile(profile, actor=admin, client=fake)
    profile.refresh_from_db()
    assert profile.status == "deleted" and profile.deleted_at
    assert any(call[0] == "delete_subject" for call in fake.calls)


@pytest.mark.django_db
@override_settings(BIOMETRIC_SEARCH_ENABLED=True)
def test_failed_remote_deletion_blocks_search_and_remains_retryable(domain):
    admin, guardian, student, school_class, _, _ = domain
    profile = enable_profile(student, school_class, actor=admin, client=FakeVision())
    with pytest.raises(RuntimeError):
        withdraw_profile(profile, actor=admin, client=FailingDeleteVision())
    profile.refresh_from_db()
    assert profile.status == "deletion_pending"
    assert not may_search_profile(guardian, profile)


@pytest.mark.django_db
def test_search_route_is_hidden_while_disabled(client, guardian):
    client.force_login(guardian)
    assert client.get("/biometrics/").status_code == 404


@pytest.mark.django_db
@override_settings(BIOMETRIC_SEARCH_ENABLED=True)
def test_collection_ids_are_opaque_and_class_scoped(domain):
    admin, _, student, school_class, _, _ = domain
    profile = enable_profile(student, school_class, actor=admin, client=FakeVision())
    assert uuid.UUID(str(profile.collection.vision_collection_id))
    assert profile.collection.school_class == school_class
