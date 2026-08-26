from datetime import UTC, timedelta

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from klasse5e.core.models import SchoolClass
from klasse5e.core.policies import has_active_membership

from .models import CalendarEntry, ICalSubscription, TimetableEntry


@login_required
def week(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id)
    if not has_active_membership(request.user, school_class):
        raise Http404
    start = timezone.localdate()
    start -= timedelta(days=start.weekday())
    end = start + timedelta(days=7)
    lessons = list(
        TimetableEntry.objects.filter(school_class=school_class).values(
            "weekday", "starts_at", "ends_at", "subject", "room"
        )
    )
    entries = list(
        CalendarEntry.objects.filter(
            school_class=school_class, starts_at__date__gte=start, starts_at__date__lt=end
        ).values("id", "kind", "title", "starts_at", "ends_at", "room", "revision", "updated_at")
    )
    return JsonResponse({"week_start": start.isoformat(), "lessons": lessons, "entries": entries})


@login_required
@require_POST
def issue_ical(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id)
    if not has_active_membership(request.user, school_class):
        raise Http404
    ICalSubscription.objects.filter(
        user=request.user, school_class=school_class, active=True
    ).update(active=False, revoked_at=timezone.now())
    _, token = ICalSubscription.issue(request.user, school_class)
    return JsonResponse({"url": f"/schedule/ical/{token}/"}, status=201)


def ical_feed(request, token):
    subscription = ICalSubscription.resolve(token)
    if not subscription or not has_active_membership(subscription.user, subscription.school_class):
        raise Http404
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Klasse 5e//Kalender//DE"]
    for entry in CalendarEntry.objects.filter(school_class=subscription.school_class).order_by(
        "starts_at"
    ):
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:calendar-{entry.id}-r{entry.revision}@klasse-5e",
                f"DTSTART:{entry.starts_at.astimezone(UTC).strftime('%Y%m%dT%H%M%SZ')}",
                f"DTEND:{entry.ends_at.astimezone(UTC).strftime('%Y%m%dT%H%M%SZ')}",
                f"SUMMARY:{entry.title.replace(chr(10), ' ')}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    response = HttpResponse("\r\n".join(lines), content_type="text/calendar; charset=utf-8")
    response["Cache-Control"] = "private, no-store"
    return response
