from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("media", "0003_photo_biometric_analysis_allowed")]

    operations = [
        migrations.AddField(
            model_name="photo",
            name="analysis_status",
            field=models.CharField(
                choices=[
                    ("not_requested", "Nicht angefordert"),
                    ("queued", "Vorgemerkt"),
                    ("analyzing", "Wird analysiert"),
                    ("ready", "Analysiert"),
                    ("review", "Prüfung nötig"),
                    ("disabled", "Nicht freigegeben"),
                ],
                default="not_requested",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="photo",
            name="ai_labels",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
