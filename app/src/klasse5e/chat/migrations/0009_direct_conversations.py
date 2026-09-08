import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def create_private_retention_category(apps, schema_editor):
    category = apps.get_model("chat", "ChatRetentionCategory")
    category.objects.update_or_create(
        name="Private Nachrichten",
        defaults={
            "retention_days": 180,
            "automatic_deletion_enabled": True,
            "intended_for_events": False,
            "is_active": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0008_merge_representative_branches"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DirectConversation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "participant_one",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="direct_conversations_as_one",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "participant_two",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="direct_conversations_as_two",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "room",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="direct_conversation",
                        to="chat.chatroom",
                    ),
                ),
                (
                    "school_class",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.schoolclass",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="directconversation",
            constraint=models.UniqueConstraint(
                fields=("school_class", "participant_one", "participant_two"),
                name="unique_direct_conversation_pair_class",
            ),
        ),
        migrations.AddConstraint(
            model_name="directconversation",
            constraint=models.CheckConstraint(
                condition=models.Q(participant_one__lt=models.F("participant_two")),
                name="direct_conversation_ordered_participants",
            ),
        ),
        migrations.RunPython(create_private_retention_category, migrations.RunPython.noop),
    ]
