from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("chat", "0006_chatroom_audience")]

    operations = [
        migrations.AlterField(
            model_name="chatroom",
            name="audience",
            field=models.CharField(
                choices=[
                    ("general", "Alle Klassenmitglieder"),
                    ("guardians", "Nur Eltern"),
                    ("students", "Nur Schülerinnen und Schüler"),
                    ("parent_representatives", "Nur Elternvertretung"),
                ],
                default="general",
                max_length=24,
            ),
        )
    ]
