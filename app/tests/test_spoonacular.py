from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from klasse5e.core.models import ClassMembership, Person, UserAccount
from klasse5e.events.models import ContributionCategory, Event
from klasse5e.events.spoonacular import Ingredient, RecipeSuggestion, SpoonacularUnavailable


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


@pytest.mark.django_db
def test_organizer_can_search_recipe_without_sending_event_data(client, guardian, breakfast_event):
    client.force_login(guardian)
    with patch(
        "klasse5e.core.ui_views.search_recipes",
        return_value=[RecipeSuggestion(recipe_id=42, title="Waffeln")],
    ) as search:
        response = client.get(f"/mehr/veranstaltungen/{breakfast_event.id}/?recipe_q=waffeln")
    assert response.status_code == 200
    assert "Waffeln" in response.content.decode()
    search.assert_called_once_with("waffeln")


@pytest.mark.django_db
def test_non_organizer_cannot_search_or_import(client, guardian, school_class, breakfast_event):
    other = UserAccount.objects.create_user("other-recipe@example.test", "Safe-Test-Password-123!")
    Person.objects.create(user=other, first_name="Andere", last_name="Person")
    ClassMembership.objects.create(
        person=other.person,
        school_class=school_class,
        valid_from=timezone.localdate(),
    )
    client.force_login(other)
    with patch("klasse5e.core.ui_views.search_recipes") as search:
        response = client.get(f"/mehr/veranstaltungen/{breakfast_event.id}/?recipe_q=waffeln")
    assert response.status_code == 200
    search.assert_not_called()
    assert client.post(f"/events/{breakfast_event.id}/recipes/42/import/").status_code == 404


@pytest.mark.django_db
def test_recipe_import_is_local_and_idempotent(client, guardian, breakfast_event):
    client.force_login(guardian)
    ingredients = [
        Ingredient(name="Mehl", amount=500, unit="g"),
        Ingredient(name="Milch", amount=1, unit="l"),
    ]
    with patch(
        "klasse5e.events.views.recipe_ingredients", return_value=("Waffeln", ingredients)
    ) as source:
        first = client.post(f"/events/{breakfast_event.id}/recipes/42/import/")
        second = client.post(f"/events/{breakfast_event.id}/recipes/42/import/")
    assert first.status_code == second.status_code == 302
    category = ContributionCategory.objects.get(source_provider="spoonacular")
    assert set(category.items.values_list("label", flat=True)) == {"Mehl", "Milch"}
    assert source.call_count == 1


@pytest.mark.django_db
def test_recipe_provider_failure_is_a_safe_ui_state(client, guardian, breakfast_event):
    client.force_login(guardian)
    with patch(
        "klasse5e.core.ui_views.search_recipes",
        side_effect=SpoonacularUnavailable("offline"),
    ):
        response = client.get(f"/mehr/veranstaltungen/{breakfast_event.id}/?recipe_q=waffeln")
    assert response.status_code == 200
    assert "nicht erreichbar" in response.content.decode()
