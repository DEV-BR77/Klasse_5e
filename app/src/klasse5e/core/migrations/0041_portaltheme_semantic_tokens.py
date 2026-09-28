from django.db import migrations, models


def tune_existing_themes(apps, schema_editor):
    PortalTheme = apps.get_model("core", "PortalTheme")
    PortalTheme.objects.filter(is_dark=False).update(
        border="#DCE3F0", success="#087A4B", warning="#A55A00", danger="#C23737"
    )
    PortalTheme.objects.filter(is_dark=True).update(
        border="#475067", success="#4FD1A5", warning="#F6C76B", danger="#FF8A9A"
    )


class Migration(migrations.Migration):
    dependencies = [("core", "0040_monitoringconfiguration")]

    operations = [
        migrations.AddField(
            model_name="portaltheme",
            name="border",
            field=models.CharField(default="#DCE3F0", max_length=7),
        ),
        migrations.AddField(
            model_name="portaltheme",
            name="success",
            field=models.CharField(default="#087A4B", max_length=7),
        ),
        migrations.AddField(
            model_name="portaltheme",
            name="warning",
            field=models.CharField(default="#A55A00", max_length=7),
        ),
        migrations.AddField(
            model_name="portaltheme",
            name="danger",
            field=models.CharField(default="#C23737", max_length=7),
        ),
        migrations.AddField(
            model_name="portaltheme",
            name="typography",
            field=models.CharField(
                choices=[
                    ("system", "Klar und neutral"),
                    ("rounded", "Freundlich und rund"),
                    ("editorial", "Ruhig und redaktionell"),
                ],
                default="system",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="portaltheme",
            name="density",
            field=models.CharField(
                choices=[
                    ("compact", "Kompakt"),
                    ("comfortable", "Ausgewogen"),
                    ("spacious", "Großzügig"),
                ],
                default="comfortable",
                max_length=16,
            ),
        ),
        migrations.RunPython(tune_existing_themes, migrations.RunPython.noop),
    ]
