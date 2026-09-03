from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from klasse5e.core.models import ClassMembership, Person, UserAccount
from klasse5e.events.models import ContributionCategory, Event
from klasse5e.events.spoonacular import FoodSuggestion, SpoonacularUnavailable, search_food_items


@pytest.fixture
def breakfast_event(db, guardian, school_class, year):
    item = Event.objects.create(
        school_class=school_class,
        school_year=year,
        title="Klassenfrühstück",
        description="Gemeinsames Frühstück",
        starts_at=timezone.now() + timedelta(days=5),
        ends_at=timezone.now() + timedelta(days=5, hours=2),
        location="Klassenraum",
        change_deadline=timezone.now() + timedelta(days=4),
        status=Event.Status.PUBLISHED,
    )
    item.organizers.add(guardian)
    return item


def test_common_german_food_groups_work_without_provider(settings):
    settings.SPOONACULAR_MAX_RESULTS = 6
    with patch("klasse5e.events.spoonacular._request") as provider:
        results = search_food_items("Obst")
    provider.assert_not_called()
    assert [item.name for item in results][:3] == ["Äpfel", "Bananen", "Weintrauben"]


def test_unknown_food_query_uses_apilayer_product_search(settings):
    settings.SPOONACULAR_MAX_RESULTS = 6
    with patch(
        "klasse5e.events.spoonacular._request",
        return_value={"products": [{"id": 42, "title": "Papaya nectar"}]},
    ) as provider:
        results = search_food_items("Papaya")
    provider.assert_called_once_with("food/products/search", {"query": "papaya", "number": "6"})
    assert results == [FoodSuggestion(source_id="42", name="Papaya nectar")]


@pytest.mark.django_db
def test_organizer_can_search_food_without_sending_event_data(client, guardian, breakfast_event):
    client.force_login(guardian)
    with patch(
        "klasse5e.core.ui_views.search_food_items",
        return_value=[FoodSuggestion(source_id="42", name="Orangensaft")],
    ) as search:
        response = client.get(f"/mehr/veranstaltungen/{breakfast_event.id}/?food_q=saft")
    assert response.status_code == 200
    assert "Orangensaft" in response.content.decode()
    search.assert_called_once_with("saft")


@pytest.mark.django_db
def test_non_organizer_cannot_search_or_import(client, guardian, school_class, breakfast_event):
    other = UserAccount.objects.create_user("other-food@example.test", "Safe-Test-Password-123!")
    Person.objects.create(user=other, first_name="Andere", last_name="Person")
    ClassMembership.objects.create(
        person=other.person,
        school_class=school_class,
        valid_from=timezone.localdate(),
    )
    client.force_login(other)
    with patch("klasse5e.core.ui_views.search_food_items") as search:
        response = client.get(f"/mehr/veranstaltungen/{breakfast_event.id}/?food_q=obst")
    assert response.status_code == 200
    search.assert_not_called()
    assert (
        client.post(
            f"/events/{breakfast_event.id}/food/42/import/",
            {"label": "Apfel", "quantity": "2", "unit": "Stück"},
        ).status_code
        == 404
    )


@pytest.mark.django_db
def test_food_item_import_is_local_and_idempotent(client, guardian, breakfast_event):
    client.force_login(guardian)
    url = f"/events/{breakfast_event.id}/food/42/import/"
    payload = {"label": "Orangensaft", "quantity": "3", "unit": "Flaschen"}
    first = client.post(url, payload)
    second = client.post(url, payload)
    assert first.status_code == second.status_code == 302
    category = ContributionCategory.objects.get(source_provider="spoonacular")
    item = category.items.get()
    assert item.label == "Orangensaft"
    assert item.desired_quantity == 3
    assert item.unit == "Flaschen"


@pytest.mark.django_db
def test_food_provider_failure_is_a_safe_ui_state(client, guardian, breakfast_event):
    client.force_login(guardian)
    with patch(
        "klasse5e.core.ui_views.search_food_items",
        side_effect=SpoonacularUnavailable("offline"),
    ):
        response = client.get(f"/mehr/veranstaltungen/{breakfast_event.id}/?food_q=papaya")
    assert response.status_code == 200
    assert "nicht erreichbar" in response.content.decode()
