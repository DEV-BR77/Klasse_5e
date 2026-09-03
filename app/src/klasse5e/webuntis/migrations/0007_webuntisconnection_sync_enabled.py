from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("webuntis", "0006_syncrun_attempt_count_and_more")]

    operations = [
        migrations.AddField(
            model_name="webuntisconnection",
            name="sync_enabled",
            field=models.BooleanField(default=True),
        ),
    ]
