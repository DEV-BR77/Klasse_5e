from django.core.management.base import BaseCommand, CommandError

from klasse5e.webuntis.models import WebUntisConnection


class Command(BaseCommand):
    help = "Assigns an external WebUntis student ID to one existing connection."

    def add_arguments(self, parser):
        parser.add_argument("--connection-id", type=int, required=True)
        parser.add_argument("--external-student-id", type=int, required=True)

    def handle(self, *args, **options):
        try:
            connection = WebUntisConnection.objects.get(pk=options["connection_id"])
        except WebUntisConnection.DoesNotExist as exc:
            raise CommandError("WebUntis connection was not found.") from exc
        connection.external_student_id = options["external_student_id"]
        connection.save(update_fields=["external_student_id", "updated_at"])
        self.stdout.write("External student ID assigned.")
