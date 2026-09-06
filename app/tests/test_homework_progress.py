from datetime import datetime, timedelta

import pytest
from django.utils import timezone

from klasse5e.core.models import ClassMembership, GuardianChildRelationship, Person
from klasse5e.webuntis.models import (
    HomeworkProgress,
    WebUntisConnection,
    WebUntisHomework,
    WebUntisLesson,
)


@pytest.fixture
def personal_homework(guardian, school_class):
    student = Person.objects.create(first_name="Mila", last_name="Beispiel")
    ClassMembership.objects.create(
        school_class=school_class,
        person=student,
        valid_from=school_class.school_year.starts_on,
    )
    GuardianChildRelationship.objects.create(
        guardian_person=guardian.person,
        student_person=student,
        relationship_type="father",
        is_legal_guardian=True,
        may_view_student_profile=True,
        valid_from=school_class.school_year.starts_on,
        status="verified",
        verified_by=guardian,
        verified_at=timezone.now(),
    )
    connection = WebUntisConnection.objects.create(
        user=guardian,
        student=student,
        username_encrypted=b"synthetic",
        password_encrypted=b"synthetic",
        status="ok",
    )
    return WebUntisHomework.objects.create(
        connection=connection,
        external_fingerprint="stable-homework-4711",
        subject="Chemie",
        assigned_on=timezone.localdate(),
        due_on=timezone.localdate() + timedelta(days=7),
        text=(
            "Du möchtest Wasser auf 50 Grad Celsius erhitzen. Nenne die Geräte, "
            "die du brauchst, und begründe ausführlich jeden einzelnen Schritt."
        ),
    )


@pytest.mark.django_db
def test_dashboard_keeps_full_homework_text_in_readable_dialog(rf, guardian, personal_homework):
    from klasse5e.core.ui_views import dashboard

    request = rf.get("/")
    request.user = guardian
    response = dashboard(request)

    assert response.status_code == 200
    assert "homework-detail-" in response.content.decode()
    assert "begründe ausführlich jeden einzelnen Schritt" in response.content.decode()
    assert "data-homework-toggle" in response.content.decode()


@pytest.mark.django_db
def test_dashboard_names_tomorrow_and_renders_a_double_lesson_time_range(
    rf, guardian, personal_homework
):
    from klasse5e.core.ui_views import _dashboard_day_copy, dashboard

    zone = timezone.get_current_timezone()
    day = timezone.localdate() + timedelta(days=1)
    for fingerprint, start_time, end_time in (
        ("dashboard-double-one", (7, 45), (8, 30)),
        ("dashboard-double-two", (8, 30), (9, 15)),
    ):
        WebUntisLesson.objects.create(
            connection=personal_homework.connection,
            external_fingerprint=fingerprint,
            subject="Geschichte",
            starts_at=timezone.make_aware(
                datetime.combine(day, datetime.min.time()).replace(
                    hour=start_time[0], minute=start_time[1]
                ),
                zone,
            ),
            ends_at=timezone.make_aware(
                datetime.combine(day, datetime.min.time()).replace(
                    hour=end_time[0], minute=end_time[1]
                ),
                zone,
            ),
        )

    request = rf.get(f"/?tag={day.isoformat()}")
    request.user = guardian
    request.session = {}
    response = dashboard(request)
    html = response.content.decode()

    copy = _dashboard_day_copy(day, today=day - timedelta(days=1))
    assert copy["dashboard_heading"] == "Was steht morgen an?"
    assert _dashboard_day_copy(day, today=day)["dashboard_heading"] == "Was steht heute an?"
    assert "Morgen" in html
    assert "07:45–09:15 Uhr" in html


@pytest.mark.django_db
def test_guardian_can_store_and_reopen_child_homework(client, guardian, personal_homework):
    client.force_login(guardian)
    url = f"/hausaufgaben/{personal_homework.id}/erledigt/"

    response = client.post(url, {"completed": "yes"})

    assert response.status_code == 200
    progress = HomeworkProgress.objects.get(
        student=personal_homework.connection.student,
        external_fingerprint=personal_homework.external_fingerprint,
    )
    assert progress.completed is True
    assert progress.completed_by == guardian
    assert progress.completed_at is not None

    response = client.post(url, {"completed": "no"})
    progress.refresh_from_db()
    assert response.status_code == 200
    assert progress.completed is False
    assert progress.completed_by is None
    assert progress.completed_at is None


@pytest.mark.django_db
def test_homework_status_cannot_be_changed_outside_own_connection(
    client, admin_user, personal_homework
):
    client.force_login(admin_user)

    response = client.post(
        f"/hausaufgaben/{personal_homework.id}/erledigt/", {"completed": "yes"}
    )

    assert response.status_code == 404
    assert not HomeworkProgress.objects.exists()
