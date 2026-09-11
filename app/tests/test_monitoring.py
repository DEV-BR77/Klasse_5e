import json

import pytest
from django.test import override_settings

from klasse5e.core.models import MonitoringComponent, MonitoringSnapshot


@pytest.mark.django_db
@override_settings(MONITORING_INGEST_TOKEN="synthetic-monitoring-token")
def test_monitoring_ingest_requires_token_and_stores_aggregate_values(client):
    response = client.post(
        "/intern/monitoring/messwerte/",
        data=json.dumps({"source": "windows", "values": {"storage": {"media": 42}}}),
        content_type="application/json",
        secure=True,
    )
    assert response.status_code == 403

    response = client.post(
        "/intern/monitoring/messwerte/",
        data=json.dumps({"source": "windows", "values": {"storage": {"media": 42}}}),
        content_type="application/json",
        headers={"X-KlassID-Monitoring-Token": "synthetic-monitoring-token"},
        secure=True,
    )
    assert response.status_code == 201
    assert MonitoringSnapshot.objects.get().values == {"storage": {"media": 42}}


@pytest.mark.django_db
@override_settings(MONITORING_INGEST_TOKEN="synthetic-monitoring-token")
def test_monitoring_state_is_idempotent(client):
    payload = json.dumps({"component": "storage_media", "state": "critical"})
    headers = {"X-KlassID-Monitoring-Token": "synthetic-monitoring-token"}
    first = client.post(
        "/intern/monitoring/zustaende/", data=payload, content_type="application/json", headers=headers, secure=True
    )
    second = client.post(
        "/intern/monitoring/zustaende/", data=payload, content_type="application/json", headers=headers, secure=True
    )
    assert first.json()["changed"] is True
    assert second.json()["changed"] is False
    assert MonitoringComponent.objects.get(component="storage_media").state == "critical"
