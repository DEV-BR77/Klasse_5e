from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0030_person_contact_visibility_defaults"),
    ]

    operations = [
        migrations.AlterField(
            model_name="roleassignment",
            name="role",
            field=models.CharField(
                choices=[
                    ("primary_admin", "Hauptadministrator"),
                    ("school_admin", "Schuladministrator"),
                    ("class_admin", "Klassenadministrator"),
                    ("deputy_admin", "Stellvertretender Administrator"),
                    ("teacher", "Lehrer"),
                    ("school_leadership", "Schulleitung"),
                    ("content_manager", "Content Manager"),
                    ("editor", "Redakteur"),
                    ("moderator", "Moderator"),
                    ("organizer", "Organisator"),
                    ("guardian", "Elternteil"),
                    ("student", "Schüler"),
                    ("parent_representative", "Elternvertretung"),
                    ("deputy_parent_representative", "Stellvertretende Elternvertretung"),
                    ("push_subscriber", "Benachrichtigungs-Abonnent"),
                ],
                max_length=32,
            ),
        ),
        migrations.RemoveConstraint(
            model_name="roleassignment",
            name="unique_user_class_role",
        ),
        migrations.AddConstraint(
            model_name="roleassignment",
            constraint=models.UniqueConstraint(
                fields=("user", "school", "school_class", "role"),
                name="unique_user_role_scope",
            ),
        ),
    ]
