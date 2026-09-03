from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("chat", "0003_chatmessage_attachment_content_type")]

    operations = [
        migrations.AddField(
            model_name="chatmessage",
            name="attachment_safety_status",
            field=models.CharField(
                choices=[
                    ("not_applicable", "Nicht erforderlich"),
                    ("pending", "Prüfung ausstehend"),
                    ("approved", "Freigegeben"),
                    ("blocked", "Gesperrt"),
                ],
                default="not_applicable",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="chatmessage",
            name="language_filter_hits",
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
