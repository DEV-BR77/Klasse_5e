from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0035_person_gender_and_more")]
    operations = [
        migrations.AddField("useraccount", "email_leak_state", models.CharField(choices=[("unknown", "Ungeprüft"), ("clear", "Keine Treffer"), ("found", "Treffer")], default="unknown", max_length=12)),
        migrations.AddField("useraccount", "email_leak_count", models.PositiveIntegerField(default=0)),
        migrations.AddField("useraccount", "email_leak_checked_at", models.DateTimeField(blank=True, null=True)),
        migrations.AddField("useraccount", "password_leak_state", models.CharField(choices=[("unknown", "Ungeprüft"), ("clear", "Keine Treffer"), ("found", "Treffer")], default="unknown", max_length=12)),
        migrations.AddField("useraccount", "password_leak_count", models.PositiveIntegerField(default=0)),
        migrations.AddField("useraccount", "password_leak_checked_at", models.DateTimeField(blank=True, null=True)),
    ]
