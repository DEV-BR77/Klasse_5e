from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("chat", "0005_room_appearance_and_optional_retention")]

    operations = [
        migrations.AddField(
            model_name="chatroom",
            name="audience",
            field=models.CharField(
                choices=[
                    ("general", "Alle Klassenmitglieder"),
                    ("guardians", "Nur Eltern"),
                    ("students", "Nur Schülerinnen und Schüler"),
                ],
                default="general",
                max_length=16,
            ),
        )
    ]
