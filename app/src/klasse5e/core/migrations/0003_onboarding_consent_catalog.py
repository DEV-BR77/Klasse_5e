import django.db.models.deletion
from django.db import migrations, models
from django.utils import timezone

CONSENTS = (
    (
        "profile_contact_visibility",
        "Kontaktdaten im Klassenprofil",
        "general",
        "profile-contact-v1",
    ),
    ("photo_gallery", "Fotos in der Klassengalerie", "photo", "photo-gallery-v1"),
    (
        "biometric_face_search",
        "Biometrische Gesichtssuche",
        "biometric",
        "biometric-face-search-v1",
    ),
    ("push_general", "Allgemeine Push-Hinweise", "general", "push-v1"),
    ("push_chat", "Push-Hinweise für Chats", "general", "push-v1"),
    ("push_events", "Push-Erinnerungen für Termine", "general", "push-v1"),
    ("webuntis_timetable", "WebUntis-Stundenplan", "general", "webuntis-v1"),
    ("webuntis_timetable_extended", "WebUntis-erweiterte Stundeninfos", "general", "webuntis-v1"),
    ("webuntis_substitutions", "WebUntis-Vertretungen", "general", "webuntis-v1"),
    ("webuntis_homework", "WebUntis-Hausaufgaben", "general", "webuntis-v1"),
    ("webuntis_exams", "WebUntis-Prüfungen", "general", "webuntis-v1"),
    ("webuntis_holidays", "WebUntis-Ferien", "general", "webuntis-v1"),
    ("webuntis_timegrid", "WebUntis-Stundenraster", "general", "webuntis-v1"),
    ("webuntis_subjects", "WebUntis-Fächer", "general", "webuntis-v1"),
    ("webuntis_rooms", "WebUntis-Räume", "general", "webuntis-v1"),
    ("webuntis_teachers", "WebUntis-Lehrkräfte", "general", "webuntis-v1"),
    ("webuntis_schoolyears", "WebUntis-Schuljahre", "general", "webuntis-v1"),
    ("webuntis_statusdata", "WebUntis-Statushinweise", "general", "webuntis-v1"),
    ("webuntis_absences", "WebUntis-Abwesenheiten", "general", "webuntis-v1"),
)


def seed_consent_catalog(apps, schema_editor):
    ConsentType = apps.get_model("core", "ConsentType")
    ConsentTextVersion = apps.get_model("core", "ConsentTextVersion")
    for key, label, category, version in CONSENTS:
        consent_type, _ = ConsentType.objects.update_or_create(
            key=key,
            defaults={
                "label": label,
                "category": category,
                "purpose": "Freiwillige, getrennt aktivierbare Funktion des Klassenportals.",
                "recipients": "Nur nach Rolle, Klasse und bestätigter Beziehung Berechtigte.",
            },
        )
        ConsentTextVersion.objects.get_or_create(
            consent_type=consent_type,
            version=version,
            defaults={
                "text": "Versionierter Fachtext; maßgeblich ist das zugehörige Datenschutzdokument.",
                "effective_from": timezone.now(),
            },
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0002_alter_useraccount_managers")]

    operations = [
        migrations.CreateModel(
            name="OnboardingState",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("current_step", models.PositiveSmallIntegerField(default=1)),
                ("identity_confirmed_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("completed_policy_version", models.CharField(blank=True, max_length=64)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="core.useraccount"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TutorialState",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("current_step", models.PositiveSmallIntegerField(default=1)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("dismissed_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="core.useraccount"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PushPreference",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("key", models.SlugField(max_length=40)),
                ("enabled", models.BooleanField(default=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.useraccount"
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=("user", "key"), name="unique_push_preference")
                ]
            },
        ),
        migrations.RunPython(seed_consent_catalog, migrations.RunPython.noop),
    ]
