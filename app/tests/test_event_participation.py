from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from klasse5e.core.models import (
    AuditEvent,
    ClassMembership,
    Household,
    Person,
    UserAccount,
    UserNotification,
)
from klasse5e.core.presentation import ensure_presentation_notifications
from klasse5e.events.models import Event, EventParticipation


@pytest.fixture
def published_event(guardian, school_class, year):
    event = Event.objects.create(
        school_class=school_class,
        school_year=year,
        title="Portalvorstellung",
        description="Wir zeigen KlassID.",
        starts_at=timezone.now() + timedelta(days=3),
        ends_at=timezone.now() + timedelta(days=3, hours=1),
        location="Online",
        change_deadline=timezone.now() + timedelta(days=2),
        status=Event.Status.PUBLISHED,
    )
    event.organizers.add(guardian)
    return event


@pytest.mark.django_db
def test_event_organizer_can_edit_and_delete_only_their_own_event(
    client, guardian, published_event, school_class
):
    client.force_login(guardian)
    response = client.post(
        reverse("ui-edit-event", args=[published_event.pk]),
        {
            "title": "KlassID vorstellen",
            "description": "Neue Beschreibung",
            "location": "Videokonferenz",
            "meeting_url": "https://meeting.example.test/portal",
            "starts_at": timezone.localtime(published_event.starts_at).strftime("%Y-%m-%dT%H:%M"),
            "ends_at": timezone.localtime(published_event.ends_at).strftime("%Y-%m-%dT%H:%M"),
        },
        secure=True,
    )
    assert response.status_code == 302
    published_event.refresh_from_db()
    assert published_event.title == "KlassID vorstellen"
    assert published_event.meeting_url == "https://meeting.example.test/portal"
    assert AuditEvent.objects.filter(action="event.updated", target_id=str(published_event.pk)).exists()

    other = UserAccount.objects.create_user("other-event@example.test", "Safe-Test-Password-123!")
    other_person = Person.objects.create(user=other, first_name="Andere", last_name="Familie")
    ClassMembership.objects.create(person=other_person, school_class=school_class, valid_from=timezone.localdate())
    client.force_login(other)
    assert client.post(reverse("ui-delete-event", args=[published_event.pk]), secure=True).status_code == 404
    assert Event.objects.filter(pk=published_event.pk).exists()

    client.force_login(guardian)
    assert client.post(reverse("ui-delete-event", args=[published_event.pk]), secure=True).status_code == 302
    assert not Event.objects.filter(pk=published_event.pk).exists()
    assert AuditEvent.objects.filter(action="event.deleted", target_id=str(published_event.pk)).exists()


@pytest.mark.django_db
def test_event_participation_shows_a_family_and_can_be_withdrawn(
    client, guardian, published_event
):
    household = Household.objects.create(label="Familie Beispiel")
    household.members.add(guardian.person)
    client.force_login(guardian)

    response = client.post(
        reverse("ui-event-attendance", args=[published_event.pk]),
        {"participating": "yes"},
        secure=True,
    )
    assert response.status_code == 302
    participation = EventParticipation.objects.get(event=published_event, user=guardian)
    assert participation.family_name == "Beispiel"
    assert AuditEvent.objects.filter(action="event.participation.created").exists()

    page = client.get(reverse("ui-event", args=[published_event.pk]), secure=True)
    assert page.status_code == 200
    assert "Wer nimmt teil?" in page.content.decode()
    assert "Beispiel" in page.content.decode()
    assert "Teilnahme zurücknehmen" in page.content.decode()

    response = client.post(
        reverse("ui-event-attendance", args=[published_event.pk]),
        {"participating": "no"},
        secure=True,
    )
    assert response.status_code == 302
    assert not EventParticipation.objects.filter(event=published_event, user=guardian).exists()
    assert AuditEvent.objects.filter(action="event.participation.withdrawn").exists()


@pytest.mark.django_db
def test_portal_presentation_is_news_and_creates_one_direct_notification(
    client, guardian, published_event
):
    client.force_login(guardian)
    ensure_presentation_notifications(guardian, published_event.school_class)

    notification = UserNotification.objects.get(user=guardian, object_id=str(published_event.pk))
    assert notification.category == "news"
    assert notification.target_url == f"/mehr/veranstaltungen/{published_event.pk}/"
    assert UserNotification.objects.filter(user=guardian).count() == 1

    response = client.get("/", secure=True)
    body = response.content.decode()
    assert "Portalvorstellung" in body
    assert f"/mehr/veranstaltungen/{published_event.pk}/" in body
    assert 'class="app-notification-badge" aria-hidden="true">1<' in body
