import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("core", "0003_onboarding_consent_catalog"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="ItslearningConnection",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("username_ciphertext", models.BinaryField()),
                ("password_ciphertext", models.BinaryField()),
                ("calendar_url_ciphertext", models.BinaryField(blank=True, default=b"")),
                ("active", models.BooleanField(default=True)),
                ("last_sync_at", models.DateTimeField(blank=True, null=True)),
                ("last_sync_status", models.CharField(default="never", max_length=32)),
                ("last_sync_message", models.CharField(blank=True, max_length=240)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "student",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="core.studentprofile"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ItslearningCourse",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("external_id", models.CharField(max_length=32)),
                ("title", models.CharField(max_length=180)),
                ("course_url", models.URLField(max_length=500)),
                ("rss_url_ciphertext", models.BinaryField(blank=True, default=b"")),
                ("report_360_url", models.URLField(blank=True, max_length=500)),
                ("learning_objectives_url", models.URLField(blank=True, max_length=500)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "connection",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="itslearning.itslearningconnection",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ItslearningUpdate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("fingerprint", models.CharField(max_length=64)),
                ("title", models.CharField(max_length=300)),
                ("summary", models.TextField(blank=True)),
                ("url", models.URLField(blank=True, max_length=800)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("first_seen_at", models.DateTimeField(auto_now_add=True)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="updates",
                        to="itslearning.itslearningcourse",
                    ),
                ),
            ],
            options={"ordering": ["-published_at", "-first_seen_at"]},
        ),
        migrations.CreateModel(
            name="ItslearningCalendarItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("uid", models.CharField(max_length=300)),
                ("title", models.CharField(max_length=300)),
                ("starts_at", models.DateTimeField()),
                ("ends_at", models.DateTimeField(blank=True, null=True)),
                ("description", models.TextField(blank=True)),
                ("url", models.URLField(blank=True, max_length=800)),
                (
                    "connection",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="calendar_items",
                        to="itslearning.itslearningconnection",
                    ),
                ),
            ],
            options={"ordering": ["starts_at"]},
        ),
        migrations.CreateModel(
            name="WebDavSpace",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("username", models.CharField(max_length=160, unique=True)),
                ("password_hash", models.CharField(max_length=256)),
                ("quota_bytes", models.PositiveBigIntegerField(default=104857600)),
                ("active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "student",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="core.studentprofile"
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="itslearningcourse",
            constraint=models.UniqueConstraint(
                fields=("connection", "external_id"), name="unique_itslearning_course"
            ),
        ),
        migrations.AddConstraint(
            model_name="itslearningupdate",
            constraint=models.UniqueConstraint(
                fields=("course", "fingerprint"), name="unique_itslearning_update"
            ),
        ),
        migrations.AddConstraint(
            model_name="itslearningcalendaritem",
            constraint=models.UniqueConstraint(
                fields=("connection", "uid"), name="unique_itslearning_calendar_item"
            ),
        ),
    ]
