from django.db import migrations, models


def disable_existing_automatic_deletion(apps, schema_editor):
    category = apps.get_model("chat", "ChatRetentionCategory")
    category.objects.update(automatic_deletion_enabled=False)


class Migration(migrations.Migration):
    dependencies = [("chat", "0004_chat_safety")]

    operations = [
        migrations.AddField(
            model_name="chatretentioncategory",
            name="automatic_deletion_enabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="chatroom",
            name="appearance",
            field=models.CharField(
                choices=[
                    ("standard", "Standard"),
                    ("classic", "Klassische Schultafel"),
                    ("modern", "Moderne Tafel"),
                    ("math", "Mathe-Tafel"),
                ],
                default="standard",
                max_length=16,
            ),
        ),
        migrations.RunPython(disable_existing_automatic_deletion, migrations.RunPython.noop),
    ]
