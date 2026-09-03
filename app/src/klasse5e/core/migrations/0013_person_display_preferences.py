from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0012_person_home_location")]
    operations = [
        migrations.AddField(model_name="person", name="chat_display_name", field=models.CharField(blank=True, max_length=80)),
        migrations.AddField(model_name="person", name="contribution_name_mode", field=models.CharField(choices=[("family", "Familienname"), ("child", "Name des Kindes"), ("personal", "Eigener Anzeigename")], default="family", max_length=16)),
    ]
