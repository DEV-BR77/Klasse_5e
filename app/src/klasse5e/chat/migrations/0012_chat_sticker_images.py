from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("chat", "0011_chatroommember")]

    operations = [
        migrations.AlterField(
            model_name="chatasset",
            name="value",
            field=models.CharField(
                blank=True,
                help_text="Emoji-Zeichen oder ein sicherer Sticker-Text/Asset-Identifier.",
                max_length=240,
            ),
        ),
        migrations.AddField(
            model_name="chatasset",
            name="image",
            field=models.ImageField(blank=True, upload_to="chat/stickers/opaque/"),
        ),
        migrations.AddField(
            model_name="chatmessage",
            name="sticker",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="messages",
                to="chat.chatasset",
            ),
        ),
    ]
