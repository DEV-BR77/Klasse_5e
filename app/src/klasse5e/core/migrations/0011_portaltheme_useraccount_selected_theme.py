import django.db.models.deletion
from django.db import migrations, models

THEMES = [
    ("modern-light", "Modern Light", "Ruhig, klar und vertraut", "adults", False, "#5558A6", "#3F427F", "#EEECFF", "#8B6BE8", "#F4F5FA", "#FFFFFF", "#25283A", "#74778A"),
    ("midnight-focus", "Midnight Focus", "Dunkel und augenschonend", "adults", True, "#8B91FF", "#B9BDFF", "#2C2F3D", "#54D6E8", "#171923", "#252830", "#F7F8FF", "#AEB4C5"),
    ("sunny-day", "Sunny Day", "Warm, freundlich und leicht", "all", False, "#C55A20", "#8D3D14", "#FFF0D8", "#F4B942", "#FFF9EF", "#FFFFFF", "#3B2C24", "#786052"),
    ("cyber-blue", "Cyber Blue", "Frisch, technisch und energiegeladen", "children", False, "#007BC2", "#005B91", "#E1F4FF", "#00A6C8", "#F0F9FF", "#FFFFFF", "#153047", "#557185"),
    ("berry-pop", "Berry Pop", "Beerig, lebendig und modern", "children", False, "#C2185B", "#8E1042", "#FCE4EC", "#7A58D6", "#FFF7FA", "#FFFFFF", "#382333", "#795C70"),
    ("comic-hero", "Comic Hero", "Kräftige Kontraste im Comic-Stil", "children", True, "#38BDF8", "#7DD3FC", "#17324D", "#F5C542", "#101B2D", "#182A42", "#FFFFFF", "#B9C8DA"),
]


def seed_themes(apps, schema_editor):
    theme = apps.get_model("core", "PortalTheme")
    fields = ("key", "name", "description", "audience", "is_dark", "primary", "primary_dark", "primary_light", "accent", "background", "surface", "text", "text_muted")
    for values in THEMES:
        theme.objects.get_or_create(key=values[0], defaults=dict(zip(fields[1:], values[1:], strict=False)))


class Migration(migrations.Migration):
    dependencies = [("core", "0010_enable_mobility_module")]
    operations = [
        migrations.CreateModel(
            name="PortalTheme",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.SlugField(unique=True)), ("name", models.CharField(max_length=80)),
                ("description", models.CharField(blank=True, max_length=180)),
                ("audience", models.CharField(choices=[("all", "Alle"), ("adults", "Eltern und Erwachsene"), ("children", "Kinder")], default="all", max_length=16)),
                ("is_dark", models.BooleanField(default=False)), ("is_active", models.BooleanField(default=True)),
                ("primary", models.CharField(default="#5558A6", max_length=7)), ("primary_dark", models.CharField(default="#3F427F", max_length=7)),
                ("primary_light", models.CharField(default="#EEECFF", max_length=7)), ("accent", models.CharField(default="#8B6BE8", max_length=7)),
                ("background", models.CharField(default="#F4F5FA", max_length=7)), ("surface", models.CharField(default="#FFFFFF", max_length=7)),
                ("text", models.CharField(default="#25283A", max_length=7)), ("text_muted", models.CharField(default="#74778A", max_length=7)),
                ("radius", models.CharField(default="1.15rem", max_length=12)), ("shadow_strength", models.PositiveSmallIntegerField(default=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
            ], options={"ordering": ["audience", "name"]},
        ),
        migrations.AddField(model_name="useraccount", name="selected_theme", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="users", to="core.portaltheme")),
        migrations.RunPython(seed_themes, migrations.RunPython.noop),
    ]
