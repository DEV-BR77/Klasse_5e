import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portal_adapters", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="portaladapter",
            name="provider",
            field=models.CharField(
                choices=[
                    ("webuntis", "WebUntis"),
                    ("itslearning", "itslearning"),
                    ("mensamax", "MensaMax"),
                    ("dsbmobile", "DSBmobile"),
                    ("mundo", "MUNDO Schule"),
                    ("wirlernenonline", "WirLernenOnline"),
                    ("wobila-bbb", "BBB Wobila"),
                    ("wobila-mail", "Mail Wobila"),
                    ("custom", "Eigenes Portal"),
                ],
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="portaladaptermodule",
            name="available_to_classes",
            field=models.ManyToManyField(
                blank=True,
                help_text="Leer bedeutet: für alle aktiven Klassen dieser Schule verfügbar.",
                related_name="available_portal_adapter_modules",
                to="core.schoolclass",
            ),
        ),
        migrations.AddField(
            model_name="portaladaptermodule",
            name="requires_child_credentials",
            field=models.BooleanField(
                default=False,
                help_text="Für dieses Modul hinterlegen Familien einen persönlichen Schulzugang beim Kind.",
            ),
        ),
        migrations.CreateModel(
            name="ChildModuleConnection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_enabled", models.BooleanField(default=False)),
                (
                    "connection_state",
                    models.CharField(
                        choices=[
                            ("not_connected", "Noch nicht verbunden"),
                            ("credentials_needed", "Zugangsdaten hinterlegen"),
                            ("connected", "Verbunden"),
                            ("external", "Extern öffnen"),
                        ],
                        default="not_connected",
                        max_length=24,
                    ),
                ),
                ("configured_at", models.DateTimeField(auto_now=True)),
                (
                    "configured_by",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
                ),
                (
                    "module",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="child_connections", to="portal_adapters.portaladaptermodule"),
                ),
                (
                    "student",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="module_connections", to="core.person"),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="childmoduleconnection",
            constraint=models.UniqueConstraint(fields=("student", "module"), name="unique_child_portal_module"),
        ),
    ]
