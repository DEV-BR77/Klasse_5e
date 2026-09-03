from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from klasse5e.core.models import ConsentType
from klasse5e.core.policies import consent_state

from .adapter import WebUntisAdapter, classify_error
from .crypto import decrypt
from .extra_models import WebUntisCalendarSubscription
from .forms import WebUntisCredentialForm
from .ical import build_calendar
from .models import WebUntisConnection
from .services import can_manage_connection, eligible_students, save_connection
from .services import remove_connection as remove_connection_service


@login_required
@require_http_methods(["GET", "POST"])
def connection(request):
    students = eligible_students(request.user)
    selected_id = request.POST.get("student") or request.GET.get("student")
    selected = students.filter(pk=selected_id).first() if selected_id else students.first()
    current = (
        WebUntisConnection.objects.filter(user=request.user, student=selected)
        .prefetch_related("features")
        .first()
        if selected
        else None
    )
    form = WebUntisCredentialForm(request.POST or None)
    if request.method == "POST" and form.is_valid() and selected:
        save_connection(
            user=request.user,
            student=selected,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        messages.success(request, "Schuldaten-Zugang eingerichtet.")
        return redirect("webuntis-connection")
    supported_keys = {
        "timetable",
        "timetable_extended",
        "substitutions",
        "homework",
        "exams",
        "holidays",
        "timegrid",
        "subjects",
        "rooms",
        "teachers",
        "schoolyears",
        "statusdata",
    }
    absence_type = ConsentType.objects.filter(key="webuntis_absences").first()
    feed_url = request.session.get(f"webuntis_feed_{current.pk}") if current else None
    return render(
        request,
        "webuntis/connection_v2.html",
        {
            "students": students,
            "selected": selected,
            "connection": current,
            "form": form,
            "capabilities": current.features.all() if current else (),
            "enabled_feature_count": (
                current.features.filter(enabled=True, key__in=supported_keys).count()
                if current
                else 0
            ),
            "feature_count": len(supported_keys),
            "latest_run": (
                current.sync_runs.order_by("-started_at").first() if current else None
            ),
            "absence_consent": (
                consent_state(absence_type, selected)
                if absence_type and selected
                else "not_allowed"
            ),
            "feed_url": feed_url,
        },
    )


@login_required
def calendar_settings(request):
    connections = list(
        WebUntisConnection.objects.filter(user=request.user)
        .select_related("student")
        .order_by("student__first_name")
    )
    rows = [
        {"connection": item, "feed_url": request.session.get(f"webuntis_feed_{item.pk}")}
        for item in connections
        if can_manage_connection(request.user, item.student)
    ]
    return render(
        request,
        "webuntis/calendar_settings.html",
        {"page_title": "Kalender verbinden", "active_section": "calendar", "rows": rows},
    )


@login_required
@require_POST
def toggle_sync(request):
    item = get_object_or_404(
        WebUntisConnection, user=request.user, pk=request.POST.get("connection_id")
    )
    if not can_manage_connection(request.user, item.student):
        raise Http404
    item.sync_enabled = request.POST.get("enabled") == "on"
    item.save(update_fields=["sync_enabled", "updated_at"])
    messages.success(
        request,
        "Automatische Synchronisierung aktiviert."
        if item.sync_enabled
        else "Automatische Synchronisierung pausiert.",
    )
    return redirect("webuntis-connection")


@login_required
@require_POST
def test_connection(request):
    item = get_object_or_404(
        WebUntisConnection, user=request.user, pk=request.POST.get("connection_id")
    )
    if not can_manage_connection(request.user, item.student):
        return redirect("webuntis-connection")
    try:
        adapter = WebUntisAdapter(
            server=item.server,
            school=item.school,
            username=decrypt(item.username_encrypted),
            password=decrypt(item.password_encrypted),
        )
        result = adapter.test_connection()
        item.mark_checked("ok", f"{len(result['methods'])} public methods detected")
        messages.success(request, "Schuldaten-Verbindung erfolgreich geprüft.")
    except Exception as exc:
        code = classify_error(exc)
        item.mark_checked(
            "mfa_required" if code == "mfa_or_sso_required" else "error",
            "Pruefung fehlgeschlagen.",
        )
        messages.error(request, "Die Schuldaten-Verbindung konnte nicht geprüft werden.")
    return redirect("webuntis-connection")


@login_required
@require_POST
def remove_connection(request):
    item = get_object_or_404(
        WebUntisConnection, user=request.user, pk=request.POST.get("connection_id")
    )
    if can_manage_connection(request.user, item.student):
        remove_connection_service(item, request.user)
        messages.success(request, "Schuldaten-Verbindung entfernt.")
    return redirect("webuntis-connection")


@login_required
@require_POST
def update_features(request):
    item = get_object_or_404(
        WebUntisConnection, user=request.user, pk=request.POST.get("connection_id")
    )
    if not can_manage_connection(request.user, item.student):
        return redirect("webuntis-connection")
    for feature in item.features.all():
        requested = request.POST.get(feature.key) == "on"
        consent_type = ConsentType.objects.filter(key=f"webuntis_{feature.key}").first()
        feature.enabled = bool(
            requested
            and consent_type
            and consent_state(consent_type, item.student) == "allowed"
        )
        feature.save(update_fields=["enabled", "updated_at"])
    messages.success(request, "Funktionsfreigaben aktualisiert.")
    return redirect("webuntis-connection")


@login_required
@require_POST
def sync_now(request):
    from .models import SyncRun
    from .sync import SyncThrottled, run_connection

    item = get_object_or_404(
        WebUntisConnection, user=request.user, pk=request.POST.get("connection_id")
    )
    if not can_manage_connection(request.user, item.student):
        return redirect("webuntis-connection")
    try:
        run = run_connection(
            item,
            trigger=SyncRun.Trigger.MANUAL,
            idempotency_key=request.POST.get("idempotency_key") or None,
        )
        if run.status == SyncRun.Status.NO_CHANGE:
            messages.success(request, "Die Schuldaten sind aktuell; keine Änderungen.")
        elif run.status == SyncRun.Status.SUCCESS:
            messages.success(
                request, f"{run.change_count} Änderungen an den Schuldaten übernommen."
            )
        elif run.status == SyncRun.Status.THROTTLED:
            messages.warning(request, "Bitte spaeter erneut versuchen.")
        else:
            messages.error(
                request,
                "Der Abruf ist fehlgeschlagen. Der Fehlercode ist im Laufstatus sichtbar.",
            )
    except SyncThrottled:
        messages.warning(request, "Der Mindestabstand zum letzten Abruf ist noch aktiv.")
    return redirect("webuntis-connection")


@login_required
def download_calendar(request, connection_id):
    item = get_object_or_404(
        WebUntisConnection, user=request.user, pk=connection_id
    )
    if not can_manage_connection(request.user, item.student):
        raise Http404
    response = HttpResponse(
        build_calendar(item), content_type="text/calendar; charset=utf-8"
    )
    response["Content-Disposition"] = 'attachment; filename="klassid-kalender.ics"'
    response["Cache-Control"] = "private, no-store"
    return response


@login_required
@require_POST
def issue_calendar(request, connection_id):
    item = get_object_or_404(
        WebUntisConnection, user=request.user, pk=connection_id
    )
    if not can_manage_connection(request.user, item.student):
        raise Http404
    WebUntisCalendarSubscription.objects.filter(
        connection=item, active=True
    ).update(active=False, revoked_at=timezone.now())
    _, token = WebUntisCalendarSubscription.issue(item)
    path = reverse("webuntis-calendar-feed", kwargs={"token": token})
    request.session[f"webuntis_feed_{item.pk}"] = request.build_absolute_uri(path)
    messages.success(request, "Neue persoenliche Kalenderadresse erstellt.")
    return redirect(
        "webuntis-calendar-settings"
        if request.POST.get("return_to") == "calendar"
        else "webuntis-connection"
    )


def calendar_feed(request, token):
    subscription = WebUntisCalendarSubscription.resolve(token)
    if not subscription or not can_manage_connection(
        subscription.connection.user, subscription.connection.student
    ):
        raise Http404
    response = HttpResponse(
        build_calendar(subscription.connection),
        content_type="text/calendar; charset=utf-8",
    )
    response["Cache-Control"] = "private, no-store"
    return response
