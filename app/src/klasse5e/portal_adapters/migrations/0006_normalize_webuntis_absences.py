from django.db import migrations


def normalize_absences(apps, schema_editor):
    PortalAdapter = apps.get_model("portal_adapters", "PortalAdapter")
    PortalAdapterModule = apps.get_model("portal_adapters", "PortalAdapterModule")

    for adapter in PortalAdapter.objects.filter(provider="webuntis"):
        module = PortalAdapterModule.objects.filter(
            adapter=adapter, key="abwesenheiten"
        ).first()
        canonical = PortalAdapterModule.objects.filter(
            adapter=adapter, key="absences"
        ).first()
        if module and canonical:
            module.delete()
        elif module:
            module.key = "absences"
            module.save(update_fields=["key"])
        else:
            PortalAdapterModule.objects.create(
                adapter=adapter,
                key="absences",
                label="Abwesenheiten",
                description=(
                    "Abwesenheiten aus WebUntis anzeigen und über den persönlichen "
                    "Zugang melden."
                ),
                is_enabled=False,
                requires_child_credentials=True,
            )


class Migration(migrations.Migration):
    dependencies = [("portal_adapters", "0005_require_single_school_integration")]
    operations = [migrations.RunPython(normalize_absences, migrations.RunPython.noop)]
