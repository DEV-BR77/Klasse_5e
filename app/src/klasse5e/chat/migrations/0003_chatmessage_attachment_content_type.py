from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("chat", "0002_retention_and_attachments")]
    operations = [migrations.AddField(model_name="chatmessage", name="attachment_content_type", field=models.CharField(blank=True, max_length=80))]
