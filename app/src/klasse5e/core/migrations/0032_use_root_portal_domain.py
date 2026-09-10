from django.db import migrations


def use_root_portal_domain(apps, schema_editor):
    ClassDomain = apps.get_model("core", "ClassDomain")
    legacy = ClassDomain.objects.filter(hostname="5e.klassid.de").first()
    if legacy is not None and not ClassDomain.objects.filter(hostname="klassid.de").exists():
        legacy.hostname = "klassid.de"
        legacy.is_reserved_exception = True
        legacy.save(update_fields=["hostname", "is_reserved_exception"])


class Migration(migrations.Migration):
    dependencies = [("core", "0031_role_scope_and_pilot_roles")]

    operations = [migrations.RunPython(use_root_portal_domain, migrations.RunPython.noop)]
