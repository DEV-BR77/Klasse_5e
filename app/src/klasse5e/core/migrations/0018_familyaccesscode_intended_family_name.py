from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0017_familyaccesscode_existing_guardian"),
    ]

    operations = [
        migrations.AddField(
            model_name="familyaccesscode",
            name="intended_family_name",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
    ]
