from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST
from .adapter import WebUntisAdapter, classify_error
from .crypto import decrypt
from .forms import WebUntisCredentialForm
from .models import WebUntisConnection
from .services import can_manage_connection, eligible_students, remove_connection, save_connection

@login_required
@require_http_methods(["GET", "POST"])
def connection(request):
    students = eligible_students(request.user)
    selected_id = request.POST.get("student") or request.GET.get("student")
    selected = students.filter(pk=selected_id).first() if selected_id else students.first()
    current = WebUntisConnection.objects.filter(user=request.user, student=selected).prefetch_related("features").first() if selected else None
    form = WebUntisCredentialForm(request.POST or None)
    if request.method == "POST" and form.is_valid() and selected:
        save_connection(user=request.user, student=selected, username=form.cleaned_data["username"], password=form.cleaned_data["password"])
        messages.success(request, "WebUntis-Zugang eingerichtet.")
        return redirect("webuntis-connection")
    return render(request, "webuntis/connection.html", {"students": students, "selected": selected, "connection": current, "form": form, "capabilities": current.features.all() if current else ()})

@login_required
@require_POST
def test_connection(request):
    item = get_object_or_404(WebUntisConnection, user=request.user, pk=request.POST.get("connection_id"))
    if not can_manage_connection(request.user, item.student):
        return redirect("webuntis-connection")
    try:
        adapter = WebUntisAdapter(server=item.server, school=item.school, username=decrypt(item.username_encrypted), password=decrypt(item.password_encrypted))
        result = adapter.test_connection()
        item.mark_checked("ok", f"{len(result['methods'])} public methods detected")
        messages.success(request, "WebUntis-Verbindung erfolgreich geprueft.")
    except Exception as exc:
        item.mark_checked("mfa_required" if classify_error(exc) == "mfa_or_sso_required" else "error", "Pruefung fehlgeschlagen.")
        messages.error(request, "WebUntis konnte nicht geprueft werden.")
    return redirect("webuntis-connection")

@login_required
@require_POST
def remove_connection(request):
    item = get_object_or_404(WebUntisConnection, user=request.user, pk=request.POST.get("connection_id"))
    if can_manage_connection(request.user, item.student):
        remove_connection(item, request.user)
        messages.success(request, "WebUntis-Verbindung entfernt.")
    return redirect("webuntis-connection")

@login_required
@require_POST
def update_features(request):
    item = get_object_or_404(WebUntisConnection, user=request.user, pk=request.POST.get("connection_id"))
    if not can_manage_connection(request.user, item.student):
        return redirect("webuntis-connection")
    for feature in item.features.all():
        feature.enabled = request.POST.get(feature.key) == "on"
        feature.save(update_fields=["enabled", "updated_at"])
    messages.success(request, "Funktionsfreigaben aktualisiert.")
    return redirect("webuntis-connection")


@login_required
@require_POST
def sync_now(request):
    from .models import SyncRun
    from .sync import SyncThrottled, run_connection
    item = get_object_or_404(WebUntisConnection, user=request.user, pk=request.POST.get("connection_id"))
    if not can_manage_connection(request.user, item.student):
        return redirect("webuntis-connection")
    try:
        run = run_connection(item, trigger=SyncRun.Trigger.MANUAL, idempotency_key=request.POST.get("idempotency_key") or None)
        if run.status == SyncRun.Status.NO_CHANGE:
            messages.success(request, "Aktuell   keine �nderungen.")
        elif run.status == SyncRun.Status.SUCCESS:
            messages.success(request, "�nderungen wurden �bernommen.")
        elif run.status == SyncRun.Status.THROTTLED:
            messages.warning(request, "Pr�fung momentan nicht m�glich; bitte sp�ter erneut versuchen.")
        else:
            messages.error(request, "WebUntis ist momentan nicht erreichbar.")
    except SyncThrottled:
        messages.warning(request, "Pr�fung momentan nicht m�glich; Mindestabstand noch nicht erreicht.")
    return redirect("webuntis-connection")

