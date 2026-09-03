from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("events", "0002_contributioncategory_source_imported_at_and_more")]
    operations = [migrations.AddField(model_name="reservation", name="fulfilled_at", field=models.DateTimeField(blank=True, null=True))]
