import hmac
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from web_push_kit import DeliveryStatus, NotificationPayload, Subscription

from klasse5e.webuntis.notifications import configured_sender

from .models import (
    MonitoringComponent,
    MonitoringSnapshot,
    PushPreference,
    PushSubscription,
    Role,
    RoleAssignment,
)
from .ui_views import _require_portal_admin

MAX_PAYLOAD_BYTES = 16 * 1024
ALLOWED_SOURCES = {"windows", "edge"}
ALLOWED_COMPONENTS = {
    "portal_https": "Portal nicht erreichbar",
    "database": "Datenbank nicht erreichbar",
    "vision": "Bildschutzdienst nicht erreichbar",
    "storage_windows": "Windows-Speicher kritisch",
    "storage_docker": "Docker-Speicher kritisch",
    "storage_database": "Datenbankspeicher kritisch",
    "storage_media": "Medien-Speicher kritisch",
    "backup": "Sicherung benötigt Prüfung",
}


def _authorized(request):
    configured = settings.MONITORING_INGEST_TOKEN
    supplied = request.headers.get("X-KlassID-Monitoring-Token", "")
    return bool(configured) and hmac.compare_digest(configured, supplied)


def _payload(request):
    if len(request.body) > MAX_PAYLOAD_BYTES:
        return None
    try:
        payload = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _notify_state_change(component, state):
    if state not in {MonitoringComponent.State.CRITICAL, MonitoringComponent.State.OK}:
        return
    sender = configured_sender()
    if sender is None:
        return
    primary_admins = RoleAssignment.objects.filter(
        active=True, role=Role.PRIMARY_ADMIN
    ).values_list("user_id", flat=True)
    opted_in = PushPreference.objects.filter(
        user_id__in=primary_admins, key="push_system_alerts", enabled=True
    ).values_list("user_id", flat=True)
    body = ALLOWED_COMPONENTS[component] if state == MonitoringComponent.State.CRITICAL else "KlassID-System wieder in Ordnung"
    for subscription in PushSubscription.objects.filter(user_id__in=opted_in, enabled=True):
        result = sender.send(
            Subscription(endpoint=subscription.endpoint, p256dh=subscription.p256dh, auth=subscription.auth),
            NotificationPayload(
                title="KlassID-Systemmeldung",
                body=body,
                url="/verwaltung/betrieb/",
                category="system_alerts",
                message_id=f"system-{component}-{state}",
            ),
        )
        if result.status == DeliveryStatus.STALE:
            subscription.delete()


@csrf_exempt
@require_POST
def monitoring_ingest(request):
    if not _authorized(request):
        return HttpResponseForbidden()
    payload = _payload(request)
    source = payload.get("source") if payload else ""
    values = payload.get("values") if payload else None
    if source not in ALLOWED_SOURCES or not isinstance(values, dict):
        return JsonResponse({"error": "invalid_payload"}, status=400)
    MonitoringSnapshot.objects.create(source=source, values=values)
    return JsonResponse({"accepted": True}, status=201)


@csrf_exempt
@require_POST
def monitoring_component_state(request):
    if not _authorized(request):
        return HttpResponseForbidden()
    payload = _payload(request)
    component = payload.get("component") if payload else ""
    state = payload.get("state") if payload else ""
    if component not in ALLOWED_COMPONENTS or state not in MonitoringComponent.State.values:
        return JsonResponse({"error": "invalid_payload"}, status=400)
    with transaction.atomic():
        item, created = MonitoringComponent.objects.select_for_update().get_or_create(component=component)
        changed = created or item.state != state
        now = timezone.now()
        item.last_reported_at = now
        if changed:
            item.state = state
            item.changed_at = now
        item.save()
    if changed:
        _notify_state_change(component, state)
    return JsonResponse({"accepted": True, "changed": changed})


@login_required
@require_GET
def monitoring_dashboard(request):
    _require_portal_admin(request.user)
    snapshots = {}
    for snapshot in MonitoringSnapshot.objects.order_by("-captured_at"):
        snapshots.setdefault(snapshot.source, snapshot)
    return render(request, "ui/monitoring_dashboard.html", {"components": MonitoringComponent.objects.all(), "snapshots": snapshots})
