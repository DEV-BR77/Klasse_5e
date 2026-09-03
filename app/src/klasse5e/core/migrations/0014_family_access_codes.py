import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0013_person_display_preferences")]
    operations = [
        migrations.CreateModel(name="FamilyAccessCode", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("batch_id", models.UUIDField()), ("serial_number", models.PositiveSmallIntegerField()), ("token_hash", models.CharField(max_length=64, unique=True)), ("expires_at", models.DateTimeField()), ("submitted_at", models.DateTimeField(blank=True, null=True)), ("completed_at", models.DateTimeField(blank=True, null=True)), ("revoked_at", models.DateTimeField(blank=True, null=True)), ("created_at", models.DateTimeField(auto_now_add=True)), ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)), ("school_class", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.schoolclass"))]),
        migrations.CreateModel(name="FamilyRegistrationRequest", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("household_label", models.CharField(max_length=120)), ("additional_adults", models.JSONField(blank=True, default=list)), ("children", models.JSONField(default=list)), ("status", models.CharField(default="email_pending", max_length=20)), ("created_at", models.DateTimeField(auto_now_add=True)), ("completed_at", models.DateTimeField(blank=True, null=True)), ("access_code", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="family_request", to="core.familyaccesscode")), ("household", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="core.household"))]),
        migrations.AddField(model_name="registrationapplication", name="family_request", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="applications", to="core.familyregistrationrequest")),
        migrations.AddField(model_name="invitation", name="family_request", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.familyregistrationrequest")),
        migrations.AddField(model_name="invitation", name="first_name", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="invitation", name="household", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.household")),
        migrations.AddField(model_name="invitation", name="last_name", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="invitation", name="school_class", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.schoolclass")),
        migrations.AddConstraint(model_name="familyaccesscode", constraint=models.UniqueConstraint(fields=("batch_id", "serial_number"), name="unique_family_code_serial")),
    ]
