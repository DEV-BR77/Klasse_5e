from django.db import migrations


CHILD_THEMES = [
    {
        "key": "princess-garden",
        "name": "Princess Garden",
        "description": "Sanfte Rosa-, Flieder- und Goldtöne mit märchenhaftem Glanz",
        "audience": "children",
        "is_dark": False,
        "primary": "#B84D87",
        "primary_dark": "#7C2F5D",
        "primary_light": "#FBE8F2",
        "accent": "#E7B94B",
        "background": "#FFF7FB",
        "surface": "#FFFFFF",
        "text": "#382536",
        "text_muted": "#876B82",
        "radius": "1.35rem",
        "shadow_strength": 12,
    },
    {
        "key": "web-hero",
        "name": "Web Hero",
        "description": "Kräftiges Rot, tiefes Blau und klare Comic-Kontraste",
        "audience": "children",
        "is_dark": False,
        "primary": "#C7353F",
        "primary_dark": "#7F1F2A",
        "primary_light": "#FDE8EA",
        "accent": "#1E5AA8",
        "background": "#F4F7FC",
        "surface": "#FFFFFF",
        "text": "#202A3A",
        "text_muted": "#61728B",
        "radius": "1rem",
        "shadow_strength": 11,
    },
]


def seed_child_themes(apps, schema_editor):
    theme = apps.get_model("core", "PortalTheme")
    for values in CHILD_THEMES:
        key = values["key"]
        defaults = {name: value for name, value in values.items() if name != "key"}
        theme.objects.get_or_create(key=key, defaults=defaults)


class Migration(migrations.Migration):
    dependencies = [("core", "0015_accountdeletionrequest_departureretentioncase")]

    operations = [migrations.RunPython(seed_child_themes, migrations.RunPython.noop)]
