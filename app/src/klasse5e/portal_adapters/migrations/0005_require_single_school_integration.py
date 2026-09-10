from django.db import migrations, models
import django.db.models.deletion


def assign_single_school(apps, schema_editor):
    Adapter = apps.get_model("portal_adapters", "PortalAdapter")
    through = Adapter.schools.through
    for adapter in Adapter.objects.all().iterator():
        school_ids = set(
            through.objects.filter(portaladapter_id=adapter.pk).values_list("school_id", flat=True)
        )
        if adapter.school_id:
            school_ids.add(adapter.school_id)
        if len(school_ids) != 1:
            raise RuntimeError(
                "PortalAdapter %s benötigt vor der Migration genau eine Schule; "
                "mehrdeutige oder unzugeordnete Adapter dürfen nicht weiter freigegeben werden."
                % adapter.pk
            )
        Adapter.objects.filter(pk=adapter.pk).update(school_id=school_ids.pop())


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0031_role_scope_and_pilot_roles"),
        ("portal_adapters", "0004_alter_portaladapter_provider_schoolmanagerconnection"),
    ]

    operations = [
        migrations.RunPython(assign_single_school, migrations.RunPython.noop),
        migrations.RemoveField(model_name="portaladapter", name="schools"),
        migrations.AlterField(
            model_name="portaladapter",
            name="school",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="portal_adapters",
                to="core.school",
            ),
        ),
        migrations.AddConstraint(
            model_name="portaladapter",
            constraint=models.UniqueConstraint(
                fields=("school", "provider", "name"),
                name="unique_portal_adapter_integration",
            ),
        ),
    ]
