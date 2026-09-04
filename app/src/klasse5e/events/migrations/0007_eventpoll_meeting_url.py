from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("events", "0006_event_meeting_url")]

    operations = [
        migrations.AddField(
            model_name="eventpoll",
            name="meeting_url",
            field=models.URLField(blank=True),
        ),
    ]
