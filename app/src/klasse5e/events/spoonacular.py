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
