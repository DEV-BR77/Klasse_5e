import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0018_familyaccesscode_intended_family_name"),
        ("webuntis", "0007_webuntisconnection_sync_enabled"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomeworkProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("external_fingerprint", models.CharField(max_length=128)),
                ("completed", models.BooleanField(default=False)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "completed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="homework_progress_updates",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="homework_progress",
                        to="core.person",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="homeworkprogress",
            constraint=models.UniqueConstraint(
                fields=("student", "external_fingerprint"),
                name="unique_student_homework_progress",
            ),
        ),
    ]
