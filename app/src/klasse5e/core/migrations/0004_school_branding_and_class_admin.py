import django.db.models.deletion
from django.db import migrations, models


def assign_default_school(apps, schema_editor):
    School = apps.get_model("core", "School")
    SchoolClass = apps.get_model("core", "SchoolClass")
    school, _ = School.objects.get_or_create(
        slug="standard-schule",
        defaults={"name": "Theodor-Heuss-Gymnasium", "short_name": "THG"},
    )
    SchoolClass.objects.filter(school__isnull=True).update(school=school)


class Migration(migrations.Migration):
    dependencies = [("core", "0003_onboarding_consent_catalog")]

    operations = [
        migrations.CreateModel(
            name="School",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("short_name", models.CharField(blank=True, max_length=64)),
                ("slug", models.SlugField(unique=True)),
                ("logo", models.ImageField(blank=True, upload_to="branding/schools/")),
                ("enabled_features", models.JSONField(blank=True, default=list)),
                ("visible_menu_items", models.JSONField(blank=True, default=list)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name="schoolclass",
            name="school",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="classes", to="core.school"),
        ),
        migrations.AddField(model_name="schoolclass", name="display_name", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="schoolclass", name="logo", field=models.ImageField(blank=True, upload_to="branding/classes/")),
        migrations.AddField(model_name="schoolclass", name="enabled_features", field=models.JSONField(blank=True, default=list)),
        migrations.AddField(model_name="schoolclass", name="visible_menu_items", field=models.JSONField(blank=True, default=list)),
        migrations.RunPython(assign_default_school, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="schoolclass",
            name="school",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="classes", to="core.school"),
        ),
        migrations.AlterField(
            model_name="roleassignment",
            name="role",
            field=models.CharField(choices=[("primary_admin", "Hauptadministrator"), ("class_admin", "Klassenadministrator"), ("deputy_admin", "Stellvertretender Administrator"), ("teacher", "Klassenlehrer"), ("editor", "Redakteur"), ("moderator", "Moderator"), ("organizer", "Organisator"), ("guardian", "Elternteil"), ("push_subscriber", "Benachrichtigungs-Abonnent")], max_length=32),
        ),
        migrations.AddConstraint(
            model_name="schoolclass",
            constraint=models.UniqueConstraint(fields=("school", "name", "school_year"), name="unique_school_class_year"),
        ),
        migrations.RemoveConstraint(model_name="schoolclass", name="unique_class_year"),
    ]
