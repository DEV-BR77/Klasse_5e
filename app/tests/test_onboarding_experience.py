from datetime import date

import pytest
from django.utils import timezone

from klasse5e.core.models import (
    ConsentDecision,
    GuardianChildRelationship,
    OnboardingState,
    Person,
    RelationshipStatus,
    StudentProfile,
)
from klasse5e.core.onboarding import current_policy_version
from klasse5e.webuntis.models import FeatureKey, WebUntisConnection, WebUntisFeaturePreference


@pytest.fixture(autouse=True)
def experience_settings(settings):
    settings.SECURE_SSL_REDIRECT = False
    settings.STORAGES = {
        **settings.STORAGES,
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }


def verify(user):
    user.email_verified_at = timezone.now()
    user.save(update_fields=["email_verified_at"])


def connect_child(guardian):
    child = Person.objects.create(first_name="Mia", last_name="Beispiel")
    StudentProfile.objects.create(person=child)
    GuardianChildRelationship.objects.create(
        guardian_person=guardian.person,
        student_person=child,
        relationship_type="father",
        is_legal_guardian=True,
        may_view_student_profile=True,
        may_manage_general_consents=True,
        may_manage_photo_consents=True,
        may_manage_biometric_consents=True,
        valid_from=date(2026, 8, 1),
        status=RelationshipStatus.VERIFIED,
        verified_at=timezone.now(),
    )
    connection = WebUntisConnection.objects.create(
        user=guardian,
        student=child,
        username_encrypted=b"encrypted-user",
        password_encrypted=b"encrypted-password",
        status="ok",
    )
    for key in FeatureKey.values:
        WebUntisFeaturePreference.objects.create(connection=connection, key=key)
    return child, connection


@pytest.mark.django_db
def test_resume_uses_saved_step_and_pause_has_accessible_landing_page(client, guardian):
    verify(guardian)
    OnboardingState.objects.create(user=guardian, current_step=4)
    client.force_login(guardian)
    response = client.get("/onboarding/")
    assert response.status_code == 200
    assert "Schritt 4 von 10" in response.content.decode()
    response = client.post("/onboarding/schritt/4/", {"action": "pause"})
    assert response.url == "/onboarding/pausiert/"
    page = client.get(response.url)
    assert page.status_code == 200
    assert "Fortschritt gespeichert" in page.content.decode()


@pytest.mark.django_db
def test_privacy_information_does_not_reset_incomplete_onboarding(client, guardian):
    verify(guardian)
    OnboardingState.objects.create(user=guardian, current_step=4)
    client.force_login(guardian)
    response = client.get("/datenschutz/")
    html = response.content.decode()
    assert response.status_code == 200
    assert "Welche Daten wofür" in html
    assert "Zurück zur Einführung" in html
    assert OnboardingState.objects.get(user=guardian).current_step == 4


@pytest.mark.django_db
def test_webuntis_step_targets_verified_child_not_guardian(client, guardian):
    verify(guardian)
    child, connection = connect_child(guardian)
    OnboardingState.objects.create(user=guardian, current_step=8)
    client.force_login(guardian)
    response = client.get("/onboarding/schritt/8/")
    html = response.content.decode()
    assert response.status_code == 200
    assert f'value="{child.id}"' in html
    assert f'value="{guardian.person.id}"' not in html
    assert "Noch kein Kalenderimport" in html
    payload = {"subject": child.id}
    payload.update(
        {
            "webuntis_timetable": "granted",
            "webuntis_timetable_extended": "denied",
            "webuntis_substitutions": "denied",
            "webuntis_homework": "denied",
            "webuntis_exams": "denied",
            "webuntis_holidays": "denied",
            "webuntis_timegrid": "denied",
            "webuntis_subjects": "denied",
            "webuntis_rooms": "denied",
            "webuntis_teachers": "denied",
            "webuntis_schoolyears": "denied",
            "webuntis_statusdata": "denied",
            "webuntis_absences": "denied",
        }
    )
    response = client.post("/onboarding/schritt/8/", payload)
    assert response.status_code == 302
    assert connection.features.get(key="timetable").enabled
    assert ConsentDecision.objects.filter(subject_person=child, decision="granted").exists()
    assert not ConsentDecision.objects.filter(
        subject_person=guardian.person, consent_type__key__startswith="webuntis_"
    ).exists()


@pytest.mark.django_db
def test_webuntis_step_without_verified_child_can_continue_safely(client, guardian):
    verify(guardian)
    state = OnboardingState.objects.create(user=guardian, current_step=8)
    client.force_login(guardian)
    response = client.post("/onboarding/schritt/8/", {})
    assert response.status_code == 302
    assert response.url == "/onboarding/schritt/9/"
    state.refresh_from_db()
    assert state.current_step == 9
    assert not ConsentDecision.objects.filter(
        deciding_person=guardian.person, consent_type__key__startswith="webuntis_"
    ).exists()


@pytest.mark.django_db
def test_disabled_biometric_step_records_safe_denial_and_continues(client, guardian):
    verify(guardian)
    state = OnboardingState.objects.create(user=guardian, current_step=9)
    client.force_login(guardian)
    response = client.post("/onboarding/schritt/9/", {})
    assert response.status_code == 302
    assert response.url == "/onboarding/schritt/10/"
    state.refresh_from_db()
    assert state.current_step == 10
    assert ConsentDecision.objects.filter(
        deciding_person=guardian.person,
        subject_person=guardian.person,
        consent_type__key="biometric_face_search",
        decision="denied",
    ).exists()


@pytest.mark.django_db
def test_completed_user_can_edit_one_feature_area(client, guardian):
    verify(guardian)
    child, _connection = connect_child(guardian)
    state = OnboardingState.objects.create(
        user=guardian,
        current_step=10,
        completed_at=timezone.now(),
        completed_policy_version=current_policy_version(),
    )
    client.force_login(guardian)
    response = client.get(f"/onboarding/schritt/8/?mode=settings&subject={child.id}")
    assert response.status_code == 200
    assert "Änderungen speichern" in response.content.decode()
    state.refresh_from_db()
    assert state.completed_at is not None


@pytest.mark.django_db
def test_tour_and_webuntis_status_explain_phase_boundary(client, guardian):
    verify(guardian)
    child, _connection = connect_child(guardian)
    OnboardingState.objects.create(
        user=guardian,
        current_step=10,
        completed_at=timezone.now(),
        completed_policy_version=current_policy_version(),
    )
    client.force_login(guardian)
    tour = client.get("/tutorial/schritt/6/").content.decode()
    assert "Noch kein Import" in tour or "noch keine Fachdaten" in tour
    assert "tour-visual--webuntis" in tour
    page = client.get(f"/mehr/webuntis/?student={child.id}")
    html = page.content.decode()
    assert page.status_code == 200
    assert "WebUntis f&uuml;r dein Kind" in html
    assert "iCal-Datei herunterladen" in html
