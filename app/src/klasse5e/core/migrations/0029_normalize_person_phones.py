import phonenumbers
from django.db import migrations


def normalize_person_phones(apps, schema_editor):
    Person = apps.get_model("core", "Person")
    for person in Person.objects.exclude(phone="").iterator():
        try:
            number = phonenumbers.parse(person.phone, "DE")
        except phonenumbers.NumberParseException as error:
            raise RuntimeError(
                "Eine bestehende Telefonnummer kann nicht sicher nach E.164 migriert werden."
            ) from error
        if number.extension or not phonenumbers.is_valid_number(number):
            raise RuntimeError(
                "Eine bestehende Telefonnummer kann nicht sicher nach E.164 migriert werden."
            )
        normalized = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
        if normalized != person.phone:
            Person.objects.filter(pk=person.pk).update(phone=normalized)


class Migration(migrations.Migration):
    dependencies = [("core", "0028_family_photo")]

    operations = [migrations.RunPython(normalize_person_phones, migrations.RunPython.noop)]
