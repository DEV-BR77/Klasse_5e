"""Minimal, non-persistent Spoonacular adapter for event planning."""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.exceptions import ValidationError


class SpoonacularUnavailable(ValidationError):
    pass


@dataclass(frozen=True)
class RecipeSuggestion:
    recipe_id: int
    title: str


@dataclass(frozen=True)
class Ingredient:
    name: str
    amount: float
    unit: str


@dataclass(frozen=True)
class FoodSuggestion:
    source_id: str
    name: str
    provider: str = "spoonacular"


LOCAL_FOOD_GROUPS = {
    "obst": ("Äpfel", "Bananen", "Weintrauben", "Mandarinen", "Beeren", "Obstsalat"),
    "frucht": ("Äpfel", "Bananen", "Weintrauben", "Mandarinen", "Beeren", "Obstsalat"),
    "getränk": ("Wasser", "Orangensaft", "Apfelsaft", "Multivitaminsaft", "Tee", "Kakao"),
    "saft": ("Orangensaft", "Apfelsaft", "Multivitaminsaft", "Traubensaft"),
    "wurst": ("Geflügelaufschnitt", "Salami", "Kochschinken", "Vegetarischer Aufschnitt"),
    "käse": ("Gouda", "Frischkäse", "Butterkäse", "Camembert", "Veganer Aufstrich"),
    "brot": ("Vollkornbrot", "Mischbrot", "Toastbrot", "Knäckebrot"),
    "brötchen": ("Weizenbrötchen", "Mehrkornbrötchen", "Laugenbrötchen", "Glutenfreie Brötchen"),
    "gebäck": ("Croissants", "Laugengebäck", "Muffins", "Kekse"),
    "frühstück": ("Brötchen", "Butter", "Marmelade", "Honig", "Käse", "Aufschnitt", "Obst", "Saft"),
}


def _request(path: str, params: dict[str, str] | None = None) -> dict:
    key = settings.SPOONACULAR_API_KEY
    if not key:
        raise SpoonacularUnavailable("spoonacular_not_configured")
    url = f"{settings.SPOONACULAR_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    if params:
        url = f"{url}?{urlencode(params)}"
    request = Request(url, headers={"apikey": key, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=settings.SPOONACULAR_API_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise SpoonacularUnavailable("spoonacular_unavailable") from error


def search_recipes(query: str) -> list[RecipeSuggestion]:
    query = query.strip()[:100]
    if not query:
        return []
    payload = _request(
        "recipes/complexSearch",
        {
            "query": query,
            "number": str(settings.SPOONACULAR_MAX_RESULTS),
            "addRecipeInformation": "false",
        },
    )
    return [
        RecipeSuggestion(recipe_id=int(item["id"]), title=str(item.get("title", "Rezept"))[:200])
        for item in payload.get("results", [])
        if item.get("id")
    ]


def search_food_items(query: str) -> list[FoodSuggestion]:
    """Return practical bring-list items; common German groups work without the provider."""
    normalized = query.strip().lower()[:100]
    if not normalized:
        return []
    local = []
    for key, labels in LOCAL_FOOD_GROUPS.items():
        if key in normalized or normalized in key:
            local.extend(labels)
    suggestions = [
        FoodSuggestion(source_id=f"local-{index}", name=name, provider="local")
        for index, name in enumerate(dict.fromkeys(local))
    ]
    if len(suggestions) >= settings.SPOONACULAR_MAX_RESULTS:
        return suggestions[: settings.SPOONACULAR_MAX_RESULTS]
    try:
        payload = _request(
            "food/ingredients/autocomplete",
            {
                "query": normalized,
                "number": str(settings.SPOONACULAR_MAX_RESULTS),
                "metaInformation": "false",
            },
        )
    except SpoonacularUnavailable:
        if suggestions:
            return suggestions
        raise
    existing = {item.name.casefold() for item in suggestions}
    for item in payload if isinstance(payload, list) else payload.get("results", []):
        name = str(item.get("name") or "").strip()[:160]
        if not name or name.casefold() in existing:
            continue
        suggestions.append(
            FoodSuggestion(source_id=str(item.get("id") or name), name=name)
        )
        existing.add(name.casefold())
    return suggestions[: settings.SPOONACULAR_MAX_RESULTS]


def recipe_ingredients(recipe_id: int) -> tuple[str, list[Ingredient]]:
    payload = _request(f"recipes/{int(recipe_id)}/information", {"includeNutrition": "false"})
    ingredients = []
    for item in payload.get("extendedIngredients", []):
        name = str(item.get("nameClean") or item.get("name") or "").strip()[:160]
        if not name:
            continue
        measures = item.get("measures", {}).get("metric", {})
        try:
            amount = float(measures.get("amount", item.get("amount", 1)))
        except (TypeError, ValueError):
            amount = 1
        ingredients.append(
            Ingredient(
                name=name,
                amount=max(amount, 0.01),
                unit=str(measures.get("unitLong") or item.get("unit") or "Stück")[:40],
            )
        )
    return str(payload.get("title", "Rezept"))[:200], ingredients
