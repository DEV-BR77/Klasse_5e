import sys

from django.core.management.base import BaseCommand, CommandError

from klasse5e.core.models import StudentProfile, UserAccount
from klasse5e.itslearning.models import ItslearningConnection


def _read_env(stream):
    values = {}
    for raw_line in stream:
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


class Command(BaseCommand):
    help = (
        "Creates an itslearning connection for explicit internal IDs. "
        "Username and password are read from stdin only."
    )

    def add_arguments(self, parser):
        parser.add_argument("--owner-id", type=int, required=True)
        parser.add_argument("--student-id", type=int, required=True)

    def handle(self, *args, **options):
        try:
            owner = UserAccount.objects.get(pk=options["owner_id"])
            student = StudentProfile.objects.get(pk=options["student_id"])
        except (UserAccount.DoesNotExist, StudentProfile.DoesNotExist) as exc:
            raise CommandError("Account or student profile was not found.") from exc

        values = _read_env(sys.stdin)
        username = values.get("Benutzer", "")
        password = values.get("Passwort", "")
        calendar_url = values.get("KalenderURL", "")
        if not username or not password:
            raise CommandError("stdin must contain Benutzer and Passwort.")

        connection, _ = ItslearningConnection.objects.get_or_create(
            student=student,
            defaults={
                "owner": owner,
                "username_ciphertext": b"",
                "password_ciphertext": b"",
            },
        )
        connection.owner = owner
        connection.set_secrets(username, password, calendar_url)
        connection.active = True
        connection.save()
        self.stdout.write("itslearning connection configured.")
