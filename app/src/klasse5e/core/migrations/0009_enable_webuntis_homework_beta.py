from django.db import migrations


def enable_homework(apps, schema_editor):
    PortalModule = apps.get_model("core", "PortalModule")
    PortalModule.objects.filter(key="webuntis_homework").update(
        stability="beta",
        default_enabled=True,
    )


def disable_homework(apps, schema_editor):
    PortalModule = apps.get_model("core", "PortalModule")
    PortalModule.objects.filter(key="webuntis_homework").update(
        stability="experimental",
        default_enabled=False,
    )


class Migration(migrations.Migration):
    dependencies = [("core", "0008_pilotreport")]
    operations = [migrations.RunPython(enable_homework, disable_homework)]
