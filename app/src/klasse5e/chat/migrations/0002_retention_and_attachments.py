import django.db.models.deletion
from django.db import migrations, models


def seed_categories(apps, schema_editor):
    category = apps.get_model("chat", "ChatRetentionCategory")
    category.objects.get_or_create(name="Freier Chat", defaults={"retention_days": 30})
    category.objects.get_or_create(name="Klassenchat", defaults={"retention_days": 90})
    category.objects.get_or_create(name="Event-Chat", defaults={"retention_days": 365, "intended_for_events": True})


class Migration(migrations.Migration):
    dependencies = [("chat", "0001_initial")]
    operations = [
        migrations.CreateModel(name="ChatRetentionCategory", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("name", models.CharField(max_length=80, unique=True)), ("retention_days", models.PositiveSmallIntegerField(default=30)), ("intended_for_events", models.BooleanField(default=False)), ("is_active", models.BooleanField(default=True))], options={"ordering": ["-intended_for_events", "retention_days", "name"]}),
        migrations.AddField(model_name="chatmessage", name="attachment", field=models.FileField(blank=True, upload_to="chat/opaque/")),
        migrations.AddField(model_name="chatmessage", name="attachment_name", field=models.CharField(blank=True, max_length=180)),
        migrations.AlterField(model_name="chatmessage", name="body", field=models.CharField(blank=True, max_length=2000)),
        migrations.AddField(model_name="chatroom", name="retention_category", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="chat.chatretentioncategory")),
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
    ]
