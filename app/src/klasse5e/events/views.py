from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from klasse5e.core.policies import has_active_membership

from .models import Event, Reservation
from .services import cancel_reservation_for_user, create_reservation


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
