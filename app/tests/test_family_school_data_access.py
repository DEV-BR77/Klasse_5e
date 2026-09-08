from datetime import datetime, timedelta

import pytest
from django.utils import timezone

from klasse5e.core.models import (
    ClassMembership,
    ConsentDecision,
    ConsentType,
    GuardianChildRelationship,
    Person,
    PortalModule,
    PortalModuleOverride,
    RoleAssignment,
    StudentProfile,
    UserAccount,
)
from klasse5e.itslearning.models import (
    ItslearningConnection,
    ItslearningCourse,
    ItslearningUpdate,
)
from klasse5e.webuntis.models import (
    WebUntisAbsence,
    WebUntisConnection,
    WebUntisHomework,
    WebUntisLesson,
)


@pytest.fixture
def shared_school_data(guardian, school_class):
    PortalModuleOverride.objects.create(
        module=PortalModule.objects.get(key="itslearning"),
        school_class=school_class,
        enabled=True,
    )
    child_user = UserAccount.objects.create_user(
        email="child-school-data@example.test", password="Synthetic-Password-123!"
    )
    child = Person.objects.create(
        user=child_user, first_name="Mila", last_name="Beispiel"
    )
    student_profile = StudentProfile.objects.create(person=child)
    ClassMembership.objects.create(
        person=child,
        school_class=school_class,
        valid_from=school_class.school_year.starts_on,
    )
    second_user = UserAccount.objects.create_user(
        email="second-guardian@example.test", password="Synthetic-Password-123!"
    )
    second_person = Person.objects.create(
        user=second_user, first_name="Sam", last_name="Beispiel"
    )
    ClassMembership.objects.create(
        person=second_person,
        school_class=school_class,
        valid_from=school_class.school_year.starts_on,
    )
    RoleAssignment.objects.create(
        user=second_user, school_class=school_class, role="guardian"
    )

    outsider = UserAccount.objects.create_user(
        email="unrelated-member@example.test", password="Synthetic-Password-123!"
    )
    outsider_person = Person.objects.create(
        user=outsider, first_name="Ohne", last_name="Beziehung"
    )
    ClassMembership.objects.create(
        person=outsider_person,
        school_class=school_class,
        valid_from=school_class.school_year.starts_on,
    )
    RoleAssignment.objects.create(user=outsider, school_class=school_class, role="guardian")

    for user in (guardian, second_user):
        GuardianChildRelationship.objects.create(
            guardian_person=user.person,
            student_person=child,
            relationship_type="guardian",
            is_legal_guardian=True,
            may_view_student_profile=True,
            may_manage_profile=user == guardian,
            may_manage_general_consents=True,
            valid_from=school_class.school_year.starts_on,
            status="verified",
            verified_by=guardian,
            verified_at=timezone.now(),
        )

    absence_consent = ConsentType.objects.get(key="webuntis_absences")
    text_version = absence_consent.consenttextversion_set.order_by(
        "-effective_from", "-id"
    ).first()
    for user in (guardian, second_user):
        ConsentDecision.objects.create(
            consent_type=absence_consent,
            text_version=text_version,
            subject_person=child,
            deciding_person=user.person,
            decision="granted",
        )

    webuntis = WebUntisConnection.objects.create(
        user=guardian,
        student=child,
        username_encrypted=b"synthetic-encrypted-user",
        password_encrypted=b"synthetic-encrypted-password",
        status="ok",
        last_successful_sync_at=timezone.now(),
    )
    start = timezone.make_aware(
        datetime.combine(timezone.localdate(), datetime.min.time()).replace(hour=8)
    )
    WebUntisLesson.objects.create(
        connection=webuntis,
        external_fingerprint="shared-lesson",
        subject="Privates Testfach",
        starts_at=start,
        ends_at=start + timedelta(minutes=45),
    )
    WebUntisHomework.objects.create(
        connection=webuntis,
        external_fingerprint="shared-homework",
        subject="Privates Testfach",
        due_on=timezone.localdate() + timedelta(days=1),
        text="Nur dem zugeordneten Kind zugängliche Testaufgabe",
    )
    WebUntisAbsence.objects.create(
        connection=webuntis,
        external_id="shared-absence",
        starts_on=timezone.localdate(),
        ends_on=timezone.localdate(),
        source_status="geteilt-geprüft",
    )

    itslearning = ItslearningConnection.objects.create(
        owner=guardian,
        student=student_profile,
        username_ciphertext=b"synthetic-encrypted-user",
        password_ciphertext=b"synthetic-encrypted-password",
        active=True,
        last_sync_status="ok",
    )
    course = ItslearningCourse.objects.create(
        connection=itslearning,
        external_id="shared-course",
        title="Privater Testkurs",
        course_url="https://wob.itslearning.com/course/test",
    )
    ItslearningUpdate.objects.create(
        course=course,
        fingerprint="shared-update",
        title="Private Lernplattform-Nachricht",
        published_at=timezone.now(),
    )
    return child_user, second_user, outsider, second_user.person


@pytest.mark.django_db
def test_child_and_each_confirmed_guardian_see_the_childs_school_data(
    client, shared_school_data
):
    child_user, second_user, _outsider, _second_person = shared_school_data

    for user in (child_user, second_user):
        client.force_login(user)
        dashboard = client.get("/", secure=True)
        assert dashboard.status_code == 200
        html = dashboard.content.decode()
        assert "Privates Testfach" in html
        assert "Nur dem zugeordneten Kind zugängliche Testaufgabe" in html

        absences = client.get("/abwesenheiten/", secure=True)
        assert absences.status_code == 200
        assert "geteilt-geprüft" in absences.content.decode()

        portal = client.get("/itslearning/", secure=True)
        assert portal.status_code == 200
        assert "Private Lernplattform-Nachricht" in portal.content.decode()


@pytest.mark.django_db
def test_school_data_stays_child_scoped_and_relationship_revocation_is_immediate(
    client, shared_school_data
):
    _child_user, second_user, outsider, second_person = shared_school_data

    client.force_login(outsider)
    assert "Privates Testfach" not in client.get("/", secure=True).content.decode()
    assert "Private Lernplattform-Nachricht" not in client.get(
        "/itslearning/", secure=True
    ).content.decode()

    GuardianChildRelationship.objects.filter(guardian_person=second_person).update(
        status="revoked"
    )
    client.force_login(second_user)
    assert "Privates Testfach" not in client.get("/", secure=True).content.decode()
    assert "Private Lernplattform-Nachricht" not in client.get(
        "/itslearning/", secure=True
    ).content.decode()


@pytest.mark.django_db
def test_shared_school_data_does_not_transfer_credential_management(
    client, shared_school_data
):
    _child_user, second_user, _outsider, _second_person = shared_school_data
    client.force_login(second_user)

    portal = client.get("/itslearning/", secure=True).content.decode()

    assert "Private Lernplattform-Nachricht" in portal
    assert "Jetzt aktualisieren" not in portal
    assert "Kurs hinzufügen" not in portal
