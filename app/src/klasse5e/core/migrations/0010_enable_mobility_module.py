from django.db import migrations


def seed_mobility(apps, schema_editor):
    PortalModule = apps.get_model("core", "PortalModule")
    PortalModule.objects.update_or_create(
        key="mobility",
        defaults={
            "label": "Mobilität und Mitfahrbörse",
            "stability": "beta",
            "default_enabled": True,
            "dependencies": [],
        },
    )


class Migration(migrations.Migration):
    dependencies = [("core", "0009_enable_webuntis_homework_beta")]
    operations = [migrations.RunPython(seed_mobility, migrations.RunPython.noop)]
