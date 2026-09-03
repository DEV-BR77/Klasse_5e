import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="MealPlan", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("source_id", models.CharField(max_length=180, unique=True)), ("iso_year", models.PositiveSmallIntegerField()), ("iso_week", models.PositiveSmallIntegerField()), ("starts_on", models.DateField()), ("ends_on", models.DateField()), ("source_url", models.URLField(max_length=1200)), ("checksum", models.CharField(max_length=64)), ("document_version", models.CharField(blank=True, max_length=80)), ("legend", models.JSONField(blank=True, default=dict)), ("status", models.CharField(choices=[("ready", "Veröffentlicht"), ("review", "Prüfung nötig"), ("failed", "Abruf fehlgeschlagen")], default="review", max_length=16)), ("parser_version", models.CharField(default="position-v1", max_length=24)), ("fetched_at", models.DateTimeField(auto_now=True)), ("error_code", models.CharField(blank=True, max_length=80))], options={"ordering": ["starts_on"]}),
        migrations.CreateModel(name="MealDay", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("date", models.DateField()), ("is_published", models.BooleanField(default=True)), ("plan", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="days", to="meals.mealplan"))], options={"ordering": ["date"]}),
        migrations.CreateModel(name="MealOption", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("line", models.PositiveSmallIntegerField()), ("components", models.JSONField(default=list)), ("additive_codes", models.JSONField(blank=True, default=list)), ("allergen_codes", models.JSONField(blank=True, default=list)), ("day", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="options", to="meals.mealday"))], options={"ordering": ["line"]}),
        migrations.AddConstraint(model_name="mealday", constraint=models.UniqueConstraint(fields=("plan", "date"), name="unique_meal_day")),
        migrations.AddConstraint(model_name="mealoption", constraint=models.UniqueConstraint(fields=("day", "line"), name="unique_meal_option")),
    ]
