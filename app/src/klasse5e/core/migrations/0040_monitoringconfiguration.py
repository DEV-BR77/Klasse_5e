from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0039_seed_phase1_role_permissions")]

    operations = [
        migrations.CreateModel(
            name="MonitoringConfiguration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_windows_enabled", models.BooleanField(default=True)),
                ("source_edge_enabled", models.BooleanField(default=True)),
                ("warning_threshold_percent", models.PositiveSmallIntegerField(default=80)),
                ("critical_threshold_percent", models.PositiveSmallIntegerField(default=90)),
                ("retention_days", models.PositiveSmallIntegerField(default=30)),
                ("cleanup_enabled", models.BooleanField(default=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Monitoring-Konfiguration",
                "verbose_name_plural": "Monitoring-Konfiguration",
            },
        ),
    ]
