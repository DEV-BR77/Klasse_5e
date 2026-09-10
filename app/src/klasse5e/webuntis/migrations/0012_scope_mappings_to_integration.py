import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portal_adapters", "0005_require_single_school_integration"),
        ("webuntis", "0011_connection_integration_scope"),
    ]

    operations = [
        migrations.AddField(
            model_name="webuntissubjectmapping",
            name="adapter",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name="webuntis_subject_mappings", to="portal_adapters.portaladapter",
            ),
        ),
        migrations.AddField(
            model_name="webuntisteachermapping",
            name="adapter",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name="webuntis_teacher_mappings", to="portal_adapters.portaladapter",
            ),
        ),
        migrations.AlterField(
            model_name="webuntissubjectmapping", name="code", field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name="webuntisteachermapping", name="code", field=models.CharField(max_length=32),
        ),
        migrations.AddConstraint(
            model_name="webuntissubjectmapping",
            constraint=models.UniqueConstraint(fields=("adapter", "code"), name="unique_webuntis_subject_mapping_integration"),
        ),
        migrations.AddConstraint(
            model_name="webuntisteachermapping",
            constraint=models.UniqueConstraint(fields=("adapter", "code"), name="unique_webuntis_teacher_mapping_integration"),
        ),
    ]
