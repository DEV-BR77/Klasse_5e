import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def initialize_code_usage(apps, schema_editor):
    FamilyAccessCode = apps.get_model("core", "FamilyAccessCode")
    FamilyAccessCode.objects.filter(submitted_at__isnull=False).update(use_count=1)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0018_familyaccesscode_intended_family_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="familyaccesscode",
            name="max_uses",
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="familyaccesscode",
            name="use_count",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.RunPython(initialize_code_usage, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="familyregistrationrequest",
            name="access_code",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="family_requests",
                to="core.familyaccesscode",
            ),
        ),
        migrations.CreateModel(
            name="FamilyChildAccount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("password_hash", models.CharField(max_length=256)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "activated_user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="family_child_setup",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "family_request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="child_accounts",
                        to="core.familyregistrationrequest",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="familychildaccount",
            constraint=models.UniqueConstraint(
                fields=("family_request", "first_name", "last_name"),
                name="unique_child_account_per_family",
            ),
        ),
    ]
