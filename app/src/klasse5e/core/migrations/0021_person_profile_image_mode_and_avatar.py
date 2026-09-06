from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0019_reusable_family_codes_and_child_accounts")]

    operations = [
        migrations.AddField(
            model_name="person",
            name="avatar_key",
            field=models.CharField(
                choices=[
                    ("peep-1", "Avatar 1"),
                    ("peep-12", "Avatar 2"),
                    ("peep-27", "Avatar 3"),
                    ("peep-46", "Avatar 4"),
                    ("peep-63", "Avatar 5"),
                    ("peep-78", "Avatar 6"),
                    ("peep-94", "Avatar 7"),
                    ("peep-101", "Avatar 8"),
                ],
                default="peep-1",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="profile_image_mode",
            field=models.CharField(
                choices=[("avatar", "Avatar"), ("photo", "Profilfoto")],
                default="avatar",
                max_length=12,
            ),
        ),
    ]
