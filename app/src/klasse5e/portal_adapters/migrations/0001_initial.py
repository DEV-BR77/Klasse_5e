import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [("core", "0019_reusable_family_codes_and_child_accounts")]

    operations = [
        migrations.CreateModel(
            name="PortalAdapter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(choices=[("mensamax", "MensaMax"), ("dsbmobile", "DSBmobile"), ("mundo", "MUNDO Schule"), ("wirlernenonline", "WirLernenOnline"), ("wobila-bbb", "BBB Wobila"), ("wobila-mail", "Mail Wobila"), ("custom", "Eigenes Portal")], max_length=32)),
                ("name", models.CharField(max_length=120)),
                ("base_url", models.URLField(blank=True)),
                ("project_identifier", models.CharField(blank=True, max_length=120)),
                ("institution_identifier", models.CharField(blank=True, max_length=120)),
                ("school_number", models.CharField(blank=True, max_length=40)),
                ("configuration_note", models.TextField(blank=True, max_length=1200)),
                ("is_enabled", models.BooleanField(default=True)),
                ("last_checked_at", models.DateTimeField(blank=True, null=True)),
                ("last_check_status", models.CharField(blank=True, max_length=32)),
                ("last_check_message", models.CharField(blank=True, max_length=300)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("school", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="portal_adapters", to="core.school")),
            ],
            options={"ordering": ("school__name", "provider", "name")},
        ),
        migrations.CreateModel(
            name="PortalAdapterModule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.SlugField(max_length=80)),
                ("label", models.CharField(max_length=120)),
                ("description", models.CharField(blank=True, max_length=300)),
                ("is_enabled", models.BooleanField(default=False)),
                ("configuration_note", models.TextField(blank=True, max_length=1200)),
                ("status", models.CharField(choices=[("not_configured", "Noch nicht angebunden"), ("ready", "Bereit zur Anbindung"), ("active", "Aktiv"), ("error", "Prüfung fehlgeschlagen")], default="not_configured", max_length=32)),
                ("last_synced_at", models.DateTimeField(blank=True, null=True)),
                ("last_sync_message", models.CharField(blank=True, max_length=300)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("adapter", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="modules", to="portal_adapters.portaladapter")),
            ],
            options={"ordering": ("label",)},
        ),
        migrations.AddConstraint(
            model_name="portaladapter",
            constraint=models.UniqueConstraint(fields=("school", "provider", "name"), name="unique_portal_adapter_per_school"),
        ),
        migrations.AddConstraint(
            model_name="portaladaptermodule",
            constraint=models.UniqueConstraint(fields=("adapter", "key"), name="unique_portal_adapter_module_key"),
        ),
    ]
