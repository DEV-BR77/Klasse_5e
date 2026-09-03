from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0011_portaltheme_useraccount_selected_theme")]
    operations = [
        migrations.AddField(model_name="person", name="home_latitude", field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
        migrations.AddField(model_name="person", name="home_longitude", field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
    ]
