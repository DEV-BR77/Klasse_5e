import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0027_reconcile_role_choices")]

    operations = [
        migrations.CreateModel(
            name="FamilyPhoto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="families/opaque/")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("household", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="photos", to="core.household")),
                ("school_class", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.schoolclass")),
                ("subjects", models.ManyToManyField(related_name="family_photos", to="core.person")),
                ("uploaded_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="core.useraccount")),
            ],
        ),
        migrations.AddConstraint(
            model_name="familyphoto",
            constraint=models.UniqueConstraint(fields=("household", "school_class"), name="unique_family_photo_per_class"),
        ),
    ]
