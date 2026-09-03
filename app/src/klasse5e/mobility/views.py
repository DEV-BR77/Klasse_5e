import secrets
from datetime import datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from klasse5e.core.models import AuditEvent, Role
from klasse5e.core.policies import active_class_for_user, active_roles

from .forms import MeetingPointForm, MobilityListingForm
from .models import (
    MobilityListing,
    MobilityListingView,
    MobilityReaction,
    MobilityReport,
    PickupDisclosure,
)
from .policies import is_verified_guardian
from .services import create_reaction, decide_reaction, revoke_pickup, share_pickup

MAP_BOUNDS = {"south": 52.329, "west": 10.623, "north": 52.509, "east": 10.913}
DEFAULT_SCHOOL_POINT = {"latitude": 52.419130, "longitude": 10.768277}


def _class_and_guardian_or_404(user):
    school_class = active_class_for_user(user)
    if school_class is None or not is_verified_guardian(user, school_class):
        raise Http404
    return school_class


def _listing_or_404(user, public_id):
    school_class = _class_and_guardian_or_404(user)
    return get_object_or_404(
        MobilityListing.objects.select_related("creator__person", "school_class__school"),
        public_id=public_id,
        school_class=school_class,
    )


def _route_points(listing):
    points = list(listing.meeting_points.filter(active=True))
    labels = [point.name for point in points]
    if listing.school_class.school.name:
        labels.append(listing.school_class.school.short_name or listing.school_class.school.name)
    count = max(len(labels), 2)
    return [
        {"x": 40 + index * (320 / (count - 1)), "y": 95 if index % 2 else 65, "label": label}
        for index, label in enumerate(labels)
    ]


def _map_school(school):
    return {
        "latitude": float(school.latitude or DEFAULT_SCHOOL_POINT["latitude"]),
        "longitude": float(school.longitude or DEFAULT_SCHOOL_POINT["longitude"]),
        "label": school.short_name or school.name,
        "kind": "school",
    }


def _map_points(listing):
    points = []
    if listing.start_latitude is not None and listing.start_longitude is not None:
        points.append(
            {
                "latitude": float(listing.start_latitude),
                "longitude": float(listing.start_longitude),
                "label": listing.approximate_area or "Startbereich",
                "kind": "start",
            }
        )
    points.extend(
        {
            "latitude": float(point.latitude),
            "longitude": float(point.longitude),
            "label": point.name,
            "kind": "meeting",
        }
        for point in listing.meeting_points.filter(
            active=True, latitude__isnull=False, longitude__isnull=False
        )
    )
    points.append(_map_school(listing.school_class.school))
    return points


def _can_moderate(user, school_class):
    return bool(
        active_roles(user, school_class)
        & {Role.MODERATOR, Role.CLASS_ADMIN, Role.SCHOOL_ADMIN, Role.PRIMARY_ADMIN}
    )


@login_required
@require_http_methods(["GET", "POST"])
def overview(request):
    school_class = _class_and_guardian_or_404(request.user)
    query = MobilityListing.objects.filter(school_class=school_class).exclude(
        status=MobilityListing.Status.WITHDRAWN
    )
    query.filter(status=MobilityListing.Status.ACTIVE, valid_until__lt=timezone.localdate()).update(
        status=MobilityListing.Status.EXPIRED
    )
    kind = request.GET.get("kind", "")
    transport = request.GET.get("transport", "")
    if kind in MobilityListing.Kind.values:
        query = query.filter(kind=kind)
    if transport in MobilityListing.Transport.values:
        query = query.filter(transport=transport)
    listings = query.annotate(reaction_count=Count("reactions")).prefetch_related("meeting_points")
    if request.method == "POST":
        form = MobilityListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.school_class = school_class
            listing.creator = request.user
            listing.save()
            AuditEvent.objects.create(
                actor=request.user,
                action="mobility.listing.created",
                target_type="mobility_listing",
                target_id=str(listing.public_id),
            )
            messages.success(request, "Der Mobilitätseintrag wurde veröffentlicht.")
            return redirect("mobility-detail", public_id=listing.public_id)
    else:
        form = MobilityListingForm(
            initial={"valid_until": timezone.localdate() + timedelta(days=30)}
        )
    return render(
        request,
        "mobility/overview.html",
        {
            "page_title": "Mobilität",
            "active_section": "mobility",
            "listings": listings,
            "form": form,
            "selected_kind": kind,
            "selected_transport": transport,
            "school_class": school_class,
            "map_bounds": MAP_BOUNDS,
            "map_school": _map_school(school_class.school),
            "map_listing_points": [
                {
                    "latitude": float(item.start_latitude),
                    "longitude": float(item.start_longitude),
                    "label": item.approximate_area or item.title,
                    "kind": item.transport,
                }
                for item in listings
                if item.start_latitude is not None and item.start_longitude is not None
            ]
            + [_map_school(school_class.school)],
        },
    )


@login_required
def detail(request, public_id):
    listing = _listing_or_404(request.user, public_id)
    if listing.creator_id != request.user.id:
        MobilityListingView.objects.get_or_create(
            listing=listing, viewer=request.user, viewed_on=timezone.localdate()
        )
    my_reaction = listing.reactions.filter(user=request.user).first()
    reactions = (
        listing.reactions.select_related("user__person")
        if listing.creator_id == request.user.id
        else []
    )
    disclosures = PickupDisclosure.objects.filter(
        listing=listing, revoked_at__isnull=True, valid_until__gt=timezone.now()
    ).filter(Q(shared_by=request.user) | Q(recipient=request.user))
    return render(
        request,
        "mobility/detail.html",
        {
            "page_title": listing.title,
            "active_section": "mobility",
            "listing": listing,
            "school_class": listing.school_class,
            "my_reaction": my_reaction,
            "reactions": reactions,
            "disclosures": disclosures,
            "route_points": _route_points(listing),
            "map_bounds": MAP_BOUNDS,
            "map_points": _map_points(listing),
            "idempotency_key": secrets.token_urlsafe(18),
            "can_moderate": _can_moderate(request.user, listing.school_class),
            "report_count": listing.reports.filter(resolved_at__isnull=True).count(),
        },
    )


@login_required
@require_POST
def add_meeting_point(request, public_id):
    listing = _listing_or_404(request.user, public_id)
    if listing.creator_id != request.user.id:
        raise Http404
    form = MeetingPointForm(request.POST)
    if form.is_valid():
        point = form.save(commit=False)
        point.listing = listing
        point.position = listing.meeting_points.count()
        point.save()
        messages.success(request, "Der öffentliche Treffpunkt wurde ergänzt.")
    else:
        messages.error(request, "Bitte prüfe die Angaben zum Treffpunkt.")
    return redirect("mobility-detail", public_id=listing.public_id)


@login_required
@require_POST
def react(request, public_id):
    listing = _listing_or_404(request.user, public_id)
    kind = request.POST.get("kind", "")
    if kind not in MobilityReaction.Kind.values:
        raise Http404
    try:
        create_reaction(
            listing=listing, user=request.user, kind=kind, message=request.POST.get("message", "")
        )
    except (PermissionDenied, ValidationError):
        raise Http404 from None
    messages.success(request, "Deine Reaktion wurde übermittelt.")
    return redirect("mobility-detail", public_id=listing.public_id)


@login_required
@require_POST
def reaction_decision(request, reaction_id):
    reaction = get_object_or_404(MobilityReaction.objects.select_related("listing"), id=reaction_id)
    try:
        decide_reaction(
            reaction=reaction, actor=request.user, decision=request.POST.get("decision", "")
        )
    except (PermissionDenied, ValidationError):
        raise Http404 from None
    return redirect("mobility-detail", public_id=reaction.listing.public_id)


@login_required
@require_POST
def change_status(request, public_id):
    listing = _listing_or_404(request.user, public_id)
    if listing.creator_id != request.user.id:
        raise Http404
    status = request.POST.get("status", "")
    if status not in {
        MobilityListing.Status.ACTIVE,
        MobilityListing.Status.PAUSED,
        MobilityListing.Status.WITHDRAWN,
    }:
        raise Http404
    listing.status = status
    listing.save(update_fields=["status", "updated_at"])
    AuditEvent.objects.create(
        actor=request.user,
        action=f"mobility.listing.{status}",
        target_type="mobility_listing",
        target_id=str(listing.public_id),
    )
    return redirect("mobility-detail", public_id=listing.public_id)


@login_required
@require_POST
def report(request, public_id):
    listing = _listing_or_404(request.user, public_id)
    if listing.creator_id == request.user.id:
        raise Http404
    MobilityReport.objects.update_or_create(
        listing=listing,
        reporter=request.user,
        defaults={"reason": request.POST.get("reason", "")[:300]},
    )
    messages.success(request, "Danke. Der Eintrag wurde zur Prüfung gemeldet.")
    return redirect("mobility-detail", public_id=listing.public_id)


@login_required
@require_POST
def disclose_pickup(request, reaction_id):
    reaction = get_object_or_404(MobilityReaction.objects.select_related("listing"), id=reaction_id)
    address = request.POST.get("exact_address", "").strip()
    if not address:
        raise Http404
    valid_until = timezone.make_aware(datetime.combine(reaction.listing.valid_until, time(23, 59)))
    try:
        share_pickup(
            reaction=reaction, actor=request.user, exact_address=address, valid_until=valid_until
        )
    except (PermissionDenied, ValidationError):
        raise Http404 from None
    messages.success(request, "Die Abholadresse wurde nur für die beteiligte Person freigegeben.")
    return redirect("mobility-detail", public_id=reaction.listing.public_id)


@login_required
@require_POST
def revoke_disclosure(request, disclosure_id):
    disclosure = get_object_or_404(
        PickupDisclosure.objects.select_related("listing"), id=disclosure_id
    )
    try:
        revoke_pickup(disclosure=disclosure, actor=request.user)
    except PermissionDenied:
        raise Http404 from None
    return redirect("mobility-detail", public_id=disclosure.listing.public_id)


@login_required
@require_POST
def moderate(request, public_id):
    listing = _listing_or_404(request.user, public_id)
    if not _can_moderate(request.user, listing.school_class):
        raise Http404
    action = request.POST.get("action", "")
    if action not in {"pause", "withdraw", "restore"}:
        raise Http404
    listing.status = {
        "pause": MobilityListing.Status.PAUSED,
        "withdraw": MobilityListing.Status.WITHDRAWN,
        "restore": MobilityListing.Status.ACTIVE,
    }[action]
    listing.save(update_fields=["status", "updated_at"])
    listing.reports.filter(resolved_at__isnull=True).update(resolved_at=timezone.now())
    AuditEvent.objects.create(
        actor=request.user,
        action=f"mobility.moderated.{action}",
        target_type="mobility_listing",
        target_id=str(listing.public_id),
    )
    messages.success(request, "Die Moderationsentscheidung wurde gespeichert.")
    return redirect("mobility-detail", public_id=listing.public_id)
