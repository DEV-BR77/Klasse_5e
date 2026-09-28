from django.db import migrations, models


def seed_chat_assets(apps, schema_editor):
    ChatAsset = apps.get_model("chat", "ChatAsset")
    values = [
        ("emoji", "Freude", "😀"),
        ("emoji", "Daumen hoch", "👍"),
        ("emoji", "Herz", "❤️"),
        ("emoji", "Applaus", "👏"),
        ("emoji", "Feier", "🎉"),
        ("sticker", "Gut gemacht", "sticker-gut-gemacht"),
        ("sticker", "Lernen", "sticker-lernen"),
    ]
    ChatAsset.objects.bulk_create(
        [ChatAsset(kind=kind, label=label, value=value, sort_order=index) for index, (kind, label, value) in enumerate(values)]
    )


class Migration(migrations.Migration):
    dependencies = [("chat", "0009_direct_conversations")]

    operations = [
        migrations.CreateModel(
            name="ChatAsset",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("emoji", "Emoji"), ("sticker", "Sticker")], max_length=12)),
                ("label", models.CharField(max_length=80)),
                ("value", models.CharField(help_text="Emoji-Zeichen oder ein sicherer Sticker-Text/Asset-Identifier.", max_length=240)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("kind", "sort_order", "label")},
        ),
        migrations.AddConstraint(
            model_name="chatasset",
            constraint=models.UniqueConstraint(fields=("kind", "label"), name="unique_chat_asset_kind_label"),
        ),
        migrations.RunPython(seed_chat_assets, migrations.RunPython.noop),
    ]
