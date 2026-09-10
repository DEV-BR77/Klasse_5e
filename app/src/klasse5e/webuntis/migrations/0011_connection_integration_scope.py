from urllib.parse import urlsplit

from django.db import migrations, models
import django.db.models.deletion


def assign_unambiguous_integrations(apps, schema_editor):
    Adapter = apps.get_model("portal_adapters", "PortalAdapter")
    Connection = apps.get_model("webuntis", "WebUntisConnection")
    adapters = list(Adapter.objects.filter(provider="webuntis"))
    for connection in Connection.objects.filter(adapter__isnull=True).iterator():
        matches = []
        for adapter in adapters:
            host = (urlsplit(adapter.base_url).hostname or "").lower()
            configured_school = (adapter.institution_identifier or "").strip()
            if host == (connection.server or "").lower() and (
                not configured_school or configured_school == connection.school
            ):
                matches.append(adapter)
        if len(matches) == 1:
            Connection.objects.filter(pk=connection.pk).update(adapter_id=matches[0].pk)
        else:
            Connection.objects.filter(pk=connection.pk).update(
                sync_enabled=False,
                status="error",
                status_detail="Schulintegration muss vor dem nächsten Abruf geprüft werden.",
            )


class Migration(migrations.Migration):
    dependencies = [
        ("portal_adapters", "0005_require_single_school_integration"),
        ("webuntis", "0010_absencesubmission"),
    ]

    operations = [
        migrations.AddField(
            model_name="webuntisconnection",
            name="adapter",
            field=models.ForeignKey(
                blank=True,
                help_text="Die geprüfte Schulintegration dieses persönlichen Zugangs.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="webuntis_connections",
                to="portal_adapters.portaladapter",
            ),
        ),
        migrations.RunPython(assign_unambiguous_integrations, migrations.RunPython.noop),
    ]
