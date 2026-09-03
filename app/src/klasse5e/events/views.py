from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from klasse5e.core.models import AuditEvent
from klasse5e.core.policies import has_active_membership

from .models import ContributionCategory, ContributionItem, Event, Reservation
from .services import cancel_reservation_for_user, create_reservation
from .spoonacular import SpoonacularUnavailable, recipe_ingredients


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id, status="published")
    if not has_active_membership(request.user, event.school_class):
        raise Http404
    return JsonResponse({"id": event.id, "title": event.title})


@login_required
@require_POST
def reserve_item(request, item_id):
    key = request.headers.get("Idempotency-Key", "")
    if not key:
        return JsonResponse({"error": "idempotency_key_required"}, status=400)
    try:
        reservation, created = create_reservation(
            item_id=item_id,
            user=request.user,
            quantity=request.POST.get("quantity", "0"),
            note=request.POST.get("note", ""),
            idempotency_key=key,
        )
    except (ValidationError, PermissionDenied):
        return JsonResponse({"error": "reservation_rejected"}, status=409)
    return JsonResponse({"id": reservation.id}, status=201 if created else 200)


@login_required
@require_POST
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    try:
        cancel_reservation_for_user(reservation, request.user)
    except (ValidationError, PermissionDenied):
        raise Http404 from None
    return HttpResponse(status=204)


def _organizer_event_or_404(request, event_id):
    event = get_object_or_404(Event, id=event_id, status=Event.Status.PUBLISHED)
    if not has_active_membership(request.user, event.school_class):
        raise Http404
    if not event.organizers.filter(id=request.user.id).exists():
        raise Http404
    return event


@login_required
@require_POST
@transaction.atomic
def import_recipe(request, event_id, recipe_id):
    event = _organizer_event_or_404(request, event_id)
    source_reference = str(recipe_id)
    existing = ContributionCategory.objects.filter(
        event=event, source_provider="spoonacular", source_reference=source_reference
    ).first()
    if existing:
        return redirect(f"/mehr/veranstaltungen/{event.id}/?recipe_status=already-imported")
    try:
        title, ingredients = recipe_ingredients(recipe_id)
    except SpoonacularUnavailable:
        return redirect(f"/mehr/veranstaltungen/{event.id}/?recipe_status=unavailable")
    if not ingredients:
        return redirect(f"/mehr/veranstaltungen/{event.id}/?recipe_status=empty")
    category = ContributionCategory.objects.create(
        event=event,
        name=f"Rezept: {title}"[:100],
        source_provider="spoonacular",
        source_reference=source_reference,
        source_title=title,
        source_imported_at=timezone.now(),
    )
    for ingredient in ingredients[:50]:
        try:
            amount = min(Decimal(str(ingredient.amount)), Decimal("999999.99"))
        except InvalidOperation:
            amount = Decimal("1")
        ContributionItem.objects.create(
            category=category,
            label=ingredient.name,
            desired_quantity=max(amount, Decimal("0.01")),
            unit=ingredient.unit or "Stück",
        )
    AuditEvent.objects.create(
        actor=request.user,
        action="event.recipe.imported",
        target_type="contribution_category",
        target_id=str(category.id),
        metadata={"event_id": event.id, "provider": "spoonacular", "recipe_id": source_reference},
    )
    return redirect(f"/mehr/veranstaltungen/{event.id}/?recipe_status=imported")


@login_required
@require_POST
@transaction.atomic
def import_food_item(request, event_id, source_id):
    event = _organizer_event_or_404(request, event_id)
    label = request.POST.get("label", "").strip()[:160]
    unit = request.POST.get("unit", "Stück").strip()[:40] or "Stück"
    try:
        quantity = min(Decimal(request.POST.get("quantity", "1")), Decimal("999999.99"))
        if quantity <= 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        return redirect(f"/mehr/veranstaltungen/{event.id}/?food_status=invalid")
    if not label:
        return redirect(f"/mehr/veranstaltungen/{event.id}/?food_status=invalid")
    category, _ = ContributionCategory.objects.get_or_create(
        event=event,
        source_provider="spoonacular",
        source_reference="food-items",
        defaults={"name": "Lebensmittel", "source_title": "Lebensmittelauswahl"},
    )
    if category.items.filter(label__iexact=label).exists():
        return redirect(f"/mehr/veranstaltungen/{event.id}/?food_status=already-added")
    item = ContributionItem.objects.create(
        category=category,
        label=label,
        desired_quantity=quantity,
        unit=unit,
    )
    AuditEvent.objects.create(
        actor=request.user,
        action="event.food_item.imported",
        target_type="contribution_item",
        target_id=str(item.id),
        metadata={"event_id": event.id, "provider": "spoonacular", "source_id": source_id[:80]},
    )
    return redirect(f"/mehr/veranstaltungen/{event.id}/?food_status=added")
