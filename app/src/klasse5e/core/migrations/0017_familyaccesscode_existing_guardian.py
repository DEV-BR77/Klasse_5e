import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0016_child_themes"),
    ]

    operations = [
        migrations.AddField(
            model_name="familyaccesscode",
            name="existing_guardian",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="linked_family_access_codes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="familyaccesscode",
            name="existing_guardian_relationship_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("mother", "Mutter"),
                    ("father", "Vater"),
                    ("guardian", "Sorgeberechtigte Person"),
                    ("foster", "Pflegeelternteil"),
                    ("step", "Stiefelternteil"),
                    ("other", "Sonstige autorisierte Bezugsperson"),
                ],
                default="",
                max_length=24,
            ),
        ),
    ]
