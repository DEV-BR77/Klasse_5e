from datetime import timedelta
from unittest.mock import Mock

import pytest
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from klasse5e.core.models import (
    ClassMembership,
    ConsentDecision,
    ConsentType,
    GuardianChildRelationship,
    Person,
    PushPreference,
    UserNotification,
)
from klasse5e.portal_adapters.models import (
    ChildModuleConnection,
    PortalAdapter,
    PortalAdapterModule,
)
from klasse5e.webuntis.absence_submission import SubmissionOutcome
from klasse5e.webuntis.absences import AbsenceDraftForm, sync_absences
from klasse5e.webuntis.models import (
    AbsenceDraft,
    AbsenceSubmission,
    WebUntisConnection,
    WebUntisFeaturePreference,
)


@pytest.fixture
def absence_connection(guardian, school_class):
    today = timezone.localdate()
    student = Person.objects.create(first_name="Synthetic", last_name="Child")
    ClassMembership.objects.create(person=student, school_class=school_class, valid_from=today)
    GuardianChildRelationship.objects.create(
        guardian_person=guardian.person,
        student_person=student,
        relationship_type="father",
        is_legal_guardian=True,
        may_view_student_profile=True,
        may_manage_general_consents=True,
        valid_from=today,
        status="verified",
        verified_at=timezone.now(),
        verified_by=guardian,
    )
    consent = ConsentType.objects.get(key="webuntis_absences")
    version = consent.consenttextversion_set.order_by("-effective_from", "-id").first()
    ConsentDecision.objects.create(
        consent_type=consent,
        text_version=version,
        subject_person=student,
        deciding_person=guardian.person,
        decision="granted",
    )
    connection = WebUntisConnection.objects.create(
        user=guardian,
        student=student,
        external_student_id=123,
        username_encrypted=b"synthetic",
        password_encrypted=b"synthetic",
    )
    WebUntisFeaturePreference.objects.create(connection=connection, key="absences", enabled=True)
    return connection


def adapter():
    return Mock(
        call_readonly=Mock(
            return_value={
                "data": {
                    "absences": [
                        {
                            "id": 7,
                            "studentId": 123,
                            "startDate": timezone.localdate().isoformat(),
                            "endDate": timezone.localdate().isoformat(),
                            "startTime": 800,
                            "endTime": 900,
                            "status": "offen",
                        }
                    ]
                }
            }
        )
    )


def enable_browser_submission(connection, school_class):
    adapter = PortalAdapter.objects.create(
        provider=PortalAdapter.Provider.WEBUNTIS,
        name="Synthetic WebUntis",
        is_enabled=True,
    )
    adapter.schools.add(school_class.school)
    module = PortalAdapterModule.objects.create(
        adapter=adapter,
        key="absences",
        label="Abwesenheiten",
        is_enabled=True,
        requires_child_credentials=True,
    )
    ChildModuleConnection.objects.create(
        student=connection.student,
        module=module,
        is_enabled=True,
        connection_state=ChildModuleConnection.ConnectionState.CONNECTED,
        configured_by=connection.user,
    )


@pytest.mark.django_db
def test_import_opt_in_and_idempotence(absence_connection):
    connection = absence_connection
    source = adapter()
    assert sync_absences(connection, source) == 1
    assert not UserNotification.objects.exists()
    PushPreference.objects.create(user=connection.user, key="inapp_absences", enabled=True)
    assert sync_absences(connection, source) == 0
    source.call_readonly.return_value["data"]["absences"][0]["id"] = 8
    assert sync_absences(connection, source) == 1
    assert sync_absences(connection, source) == 0
    notification = UserNotification.objects.get()
    assert notification.category == "absences"
    assert "Synthetic" not in notification.summary
    source.call_readonly.return_value["data"]["absences"][0]["status"] = "entschuldigt"
    assert sync_absences(connection, source) == 1
    assert UserNotification.objects.count() == 1


@pytest.mark.django_db
def test_foreign_payload_rolls_back(absence_connection):
    source = adapter()
    source.call_readonly.return_value["data"]["absences"].append({"id": 8, "studentId": 999})
    with pytest.raises(ValueError):
        sync_absences(absence_connection, source)
    assert not absence_connection.absences.exists()


@pytest.mark.django_db
@pytest.mark.parametrize("revocation", ["relationship", "consent", "membership", "account"])
def test_revocation_prevents_reads_and_import(client, absence_connection, revocation):
    connection = absence_connection
    client.force_login(connection.user)
    assert client.get("/abwesenheiten/").status_code == 200
    if revocation == "relationship":
        GuardianChildRelationship.objects.filter(student_person=connection.student).update(
            valid_until=timezone.localdate() - timedelta(days=1)
        )
    elif revocation == "consent":
        ConsentDecision.objects.filter(subject_person=connection.student).update(
            revoked_at=timezone.now()
        )
    elif revocation == "membership":
        ClassMembership.objects.filter(person=connection.student).update(status="inactive")
    else:
        connection.user.is_active = False
        connection.user.save()
    assert client.get("/abwesenheiten/").status_code in (302, 403, 404)
    source = adapter()
    with pytest.raises(PermissionDenied):
        sync_absences(connection, source)
    source.call_readonly.assert_not_called()


@pytest.mark.django_db
def test_local_draft_and_foreign_child_rejection(client, absence_connection):
    connection = absence_connection
    client.force_login(connection.user)
    response = client.get("/abwesenheiten/")
    assert response["Cache-Control"] == "private, no-store"
    assert response.context["form"]["starts_on"].value() == timezone.localdate()
    data = dict(
        student=connection.student_id,
        starts_on=timezone.localdate(),
        ends_on=timezone.localdate(),
        reason="sick",
        note="<script>private</script>",
    )
    assert client.post("/abwesenheiten/", data).status_code == 302
    assert AbsenceDraft.objects.get().user == connection.user
    response = client.get("/abwesenheiten/")
    assert b"&lt;script&gt;private&lt;/script&gt;" in response.content
    assert "Nicht übertragen" in response.content.decode()
    data["student"] = Person.objects.create(first_name="Other").pk
    client.post("/abwesenheiten/", data)
    assert AbsenceDraft.objects.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("end,st,et", [("2026-09-07", "", ""), ("2026-09-08", "10:00", "09:00")])
def test_invalid_intervals(end, st, et, absence_connection):
    from klasse5e.webuntis.absences import child_contexts

    form = AbsenceDraftForm(
        dict(
            student=absence_connection.student_id,
            starts_on="2026-09-08",
            ends_on=end,
            starts_time=st,
            ends_time=et,
            reason="sick",
        ),
        children=child_contexts(absence_connection.user),
    )
    assert not form.is_valid()


@pytest.mark.django_db
def test_preference_table_and_save(client, absence_connection):
    from klasse5e.core.views import _notification_rows

    user = absence_connection.user
    row = next(r for r in _notification_rows(user) if r["key"] == "absences")
    assert row["inapp"] is False
    client.force_login(user)
    response = client.post(
        "/einstellungen/profil/", {"save_scope": "notifications", "inapp_absences": "on"}
    )
    assert response.status_code == 302
    assert PushPreference.objects.get(user=user, key="inapp_absences").enabled


@pytest.mark.django_db
def test_draft_delete_and_retention(client, absence_connection):
    from django.core.management import call_command

    c = absence_connection
    client.force_login(c.user)
    draft = AbsenceDraft.objects.create(user=c.user, student=c.student, reason="other")
    response = client.post("/abwesenheiten/", {"action": "delete", "draft_id": draft.pk})
    assert response.status_code == 302
    assert not AbsenceDraft.objects.exists()
    draft = AbsenceDraft.objects.create(user=c.user, student=c.student, reason="other")
    submission = AbsenceSubmission.objects.create(
        token="00000000-0000-0000-0000-000000000001",
        user=c.user,
        student=c.student,
        fingerprint="a" * 64,
    )
    AbsenceDraft.objects.filter(pk=draft.pk).update(created_at=timezone.now() - timedelta(days=31))
    AbsenceSubmission.objects.filter(pk=submission.pk).update(
        created_at=timezone.now() - timedelta(days=31)
    )
    sync_absences(c, adapter())
    call_command("purge_absences")
    assert not AbsenceDraft.objects.exists()
    assert not AbsenceSubmission.objects.exists()
    assert c.absences.exists()
    ConsentDecision.objects.filter(subject_person=c.student).update(revoked_at=timezone.now())
    call_command("purge_absences")
    assert not c.absences.exists()


@pytest.mark.django_db
def test_browser_submission_is_explicit_idempotent_and_neutral(client, absence_connection, school_class, monkeypatch):
    enable_browser_submission(absence_connection, school_class)
    client.force_login(absence_connection.user)
    response = client.get("/abwesenheiten/")
    form = response.context["submission_form"]
    assert form is not None
    assert str(absence_connection.student_id) in response.content.decode()
    submitted = []

    def fake_submit(connection, expected, user):
        submitted.append((connection.pk, expected.student_key, user.pk))
        return SubmissionOutcome.CONFIRMED

    monkeypatch.setattr("klasse5e.webuntis.absences._submit_browser", fake_submit)
    data = {
        "action": "submit",
        "submission-student": absence_connection.student_id,
        "submission-starts_on": "2026-09-10",
        "submission-ends_on": "2026-09-10",
        "submission-starts_time": "08:00",
        "submission-ends_time": "17:00",
        "submission-note": "Synthetic private note",
        "submission-token": form["token"].value(),
    }
    response = client.post("/abwesenheiten/", data)
    assert response.status_code == 302
    assert len(submitted) == 1
    submission = AbsenceSubmission.objects.get()
    assert submission.status == "confirmed"
    assert "Synthetic private note" not in submission.fingerprint
    assert client.post("/abwesenheiten/", data).status_code == 302
    assert len(submitted) == 1


@pytest.mark.django_db
def test_browser_submission_denies_disabled_adapter(client, absence_connection):
    client.force_login(absence_connection.user)
    response = client.get("/abwesenheiten/")
    assert response.context["submission_form"] is None


@pytest.mark.django_db
def test_browser_start_failure_is_neutral_and_never_reports_confirmation(
    client, absence_connection, school_class, monkeypatch
):
    enable_browser_submission(absence_connection, school_class)
    client.force_login(absence_connection.user)
    form = client.get("/abwesenheiten/").context["submission_form"]
    monkeypatch.setattr(
        "klasse5e.webuntis.absences._submit_browser", Mock(side_effect=RuntimeError("private detail"))
    )
    response = client.post(
        "/abwesenheiten/",
        {
            "action": "submit",
            "submission-student": absence_connection.student_id,
            "submission-starts_on": "2026-09-10",
            "submission-ends_on": "2026-09-10",
            "submission-starts_time": "08:00",
            "submission-ends_time": "17:00",
            "submission-note": "",
            "submission-token": form["token"].value(),
        },
    )
    result = client.get(response.url)
    assert AbsenceSubmission.objects.get().status == "not_sent"
    assert "private detail" not in result.content.decode()
    assert "nicht übermittelt" in result.content.decode()


@pytest.mark.django_db
def test_post_requires_csrf(absence_connection):
    from django.test import Client

    client = Client(enforce_csrf_checks=True)
    client.force_login(absence_connection.user)
    assert client.post("/abwesenheiten/", {}).status_code == 403


@pytest.mark.django_db
def test_notification_access_via_child_membership(client, absence_connection):
    c = absence_connection
    PushPreference.objects.create(user=c.user, key="inapp_absences", enabled=True)
    sync_absences(c, adapter())
    ClassMembership.objects.filter(person=c.user.person).delete()
    client.force_login(c.user)
    response = client.get("/benachrichtigungen/")
    assert response.status_code == 200
    assert "Neue Abwesenheit" in response.content.decode()
