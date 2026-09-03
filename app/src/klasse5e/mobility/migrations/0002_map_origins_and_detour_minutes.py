import django.core.validators
from django.db import migrations, models


def configure_thg_location(apps, schema_editor):
    School = apps.get_model("core", "School")
    School.objects.filter(name__icontains="Theodor-Heuss").update(
        address="Martin-Luther-Straße 23",
        postal_code="38440",
        city="Wolfsburg",
        latitude=52.419130,
        longitude=10.768277,
        location_valid=True,
    )


class Migration(migrations.Migration):
    dependencies = [("mobility", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="mobilitylisting",
            name="start_latitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name="mobilitylisting",
            name="start_longitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name="mobilitylisting",
            name="max_detour_minutes",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(60),
                ],
            ),
        ),
        migrations.RunPython(configure_thg_location, migrations.RunPython.noop),
    ]
