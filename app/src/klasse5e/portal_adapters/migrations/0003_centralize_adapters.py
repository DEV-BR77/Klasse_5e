import django.db.models.deletion
from django.db import migrations, models


def copy_legacy_school(apps, schema_editor):
    Adapter = apps.get_model("portal_adapters", "PortalAdapter")
    for adapter in Adapter.objects.exclude(school_id=None):
        adapter.schools.add(adapter.school_id)


class Migration(migrations.Migration):
    dependencies = [("portal_adapters", "0002_child_module_connections")]

    operations = [
        migrations.RemoveConstraint(
            model_name="portaladapter", name="unique_portal_adapter_per_school"
        ),
        migrations.AlterField(
            model_name="portaladapter",
            name="school",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="legacy_portal_adapters", to="core.school"),
        ),
        migrations.AddField(
            model_name="portaladapter",
            name="schools",
            field=models.ManyToManyField(blank=True, related_name="available_portal_adapters", to="core.school"),
        ),
        migrations.AddField(
            model_name="portaladapter",
            name="requires_child_credentials",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(copy_legacy_school, migrations.RunPython.noop),
        migrations.AlterModelOptions(name="portaladapter", options={"ordering": ("name", "provider")}),
    ]
