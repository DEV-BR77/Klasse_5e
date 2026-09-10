from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0029_normalize_person_phones"),
    ]

    operations = [
        migrations.AlterField(
            model_name="person",
            name="email_visibility",
            field=models.CharField(
                choices=[
                    ("self", "Nur eigene Person"),
                    ("admins", "Administratoren"),
                    ("teachers", "Klassenlehrer und Administratoren"),
                    ("members", "Aktive Klassenmitglieder"),
                    ("hidden", "Nicht sichtbar"),
                ],
                default="members",
                max_length=16,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="phone_visibility",
            field=models.CharField(
                choices=[
                    ("self", "Nur eigene Person"),
                    ("admins", "Administratoren"),
                    ("teachers", "Klassenlehrer und Administratoren"),
                    ("members", "Aktive Klassenmitglieder"),
                    ("hidden", "Nicht sichtbar"),
                ],
                default="members",
                max_length=16,
            ),
        ),
    ]
