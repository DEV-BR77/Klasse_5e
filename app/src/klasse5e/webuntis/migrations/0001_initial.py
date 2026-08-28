import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("core", "0002_alter_useraccount_managers")]
    operations = [
        migrations.CreateModel(
            name="WebUntisConnection",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("server", models.CharField(default="thgwob.webuntis.com", max_length=255)),
                ("school", models.CharField(default="thgwob", max_length=80)),
                ("username_encrypted", models.BinaryField()),
                ("password_encrypted", models.BinaryField()),
                ("status", models.CharField(default="not_tested", max_length=24)),
                ("status_detail", models.CharField(blank=True, max_length=160)),
                ("last_checked_at", models.DateTimeField(blank=True, null=True)),
                ("last_successful_sync_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="webuntis_connections",
                        to="core.person",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="webuntis_connections",
                        to="core.useraccount",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("user", "student"), name="unique_webuntis_user_student"
                    )
                ]
            },
        ),
        migrations.CreateModel(
            name="WebUntisFeaturePreference",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("key", models.CharField(max_length=40)),
                ("enabled", models.BooleanField(default=False)),
                ("state", models.CharField(default="not_checked", max_length=24)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "connection",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="features",
                        to="webuntis.webuntisconnection",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("connection", "key"), name="unique_webuntis_feature"
                    )
                ]
            },
        ),
        migrations.CreateModel(
            name="WebUntisLesson",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("external_fingerprint", models.CharField(max_length=128)),
                ("starts_at", models.DateTimeField()),
                ("ends_at", models.DateTimeField()),
                ("subject", models.CharField(blank=True, max_length=100)),
                ("room", models.CharField(blank=True, max_length=60)),
                ("teacher_label", models.CharField(blank=True, max_length=100)),
                ("status", models.CharField(default="regular", max_length=24)),
                ("source_updated_at", models.DateTimeField(blank=True, null=True)),
                ("fetched_at", models.DateTimeField(auto_now=True)),
                ("visibility", models.CharField(default="personal", max_length=12)),
                ("delete_after", models.DateTimeField(blank=True, null=True)),
                (
                    "connection",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lessons",
                        to="webuntis.webuntisconnection",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("connection", "external_fingerprint"),
                        name="unique_webuntis_lesson_fingerprint",
                    )
                ]
            },
        ),
        migrations.CreateModel(
            name="WebUntisHomework",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("external_fingerprint", models.CharField(max_length=128)),
                ("subject", models.CharField(blank=True, max_length=100)),
                ("assigned_on", models.DateField(blank=True, null=True)),
                ("due_on", models.DateField(blank=True, null=True)),
                ("text", models.TextField(blank=True)),
                ("source_status", models.CharField(blank=True, max_length=40)),
                ("fetched_at", models.DateTimeField(auto_now=True)),
                ("visibility", models.CharField(default="personal", max_length=12)),
                ("delete_after", models.DateTimeField(blank=True, null=True)),
                (
                    "connection",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="homework",
                        to="webuntis.webuntisconnection",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("connection", "external_fingerprint"),
                        name="unique_webuntis_homework_fingerprint",
                    )
                ]
            },
        ),
    ]
