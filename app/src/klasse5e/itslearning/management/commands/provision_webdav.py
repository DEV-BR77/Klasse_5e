import sys

from django.core.management.base import BaseCommand, CommandError

from klasse5e.core.models import StudentProfile
from klasse5e.itslearning.models import WebDavSpace


class Command(BaseCommand):
    help = "Creates a per-student WebDAV space using a password read from stdin."

    def add_arguments(self, parser):
        parser.add_argument("--student-id", type=int, required=True)
        parser.add_argument("--username", required=True)

    def handle(self, *args, **options):
        try:
            student = StudentProfile.objects.get(pk=options["student_id"])
        except StudentProfile.DoesNotExist as exc:
            raise CommandError("Student profile was not found.") from exc

        password = sys.stdin.readline().rstrip("\r\n")
        if len(password) < 12:
            raise CommandError("WebDAV password is too short.")

        space, _ = WebDavSpace.objects.get_or_create(
            student=student,
            defaults={"username": options["username"], "password_hash": ""},
        )
        space.username = options["username"]
        space.set_password(password)
        space.quota_bytes = 100 * 1024 * 1024
        space.active = True
        space.save()
        self.stdout.write("WebDAV space configured with a 100 MiB quota.")
