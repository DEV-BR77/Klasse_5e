from django.core.management.base import BaseCommand, CommandError

from klasse5e.webuntis.models import WebUntisConnection
from klasse5e.webuntis.reference_mapping import apply_reference_mapping


class Command(BaseCommand):
    help = "Maps numeric WebUntis lesson identifiers using private local reference exports."

    def add_arguments(self, parser):
        parser.add_argument("--timetable", required=True)
        parser.add_argument("--class-mappings", required=True)
        parser.add_argument("--connection-id", type=int)

    def handle(self, *args, **options):
        connections = WebUntisConnection.objects.all()
        if options["connection_id"]:
            connections = connections.filter(pk=options["connection_id"])
        if not connections.exists():
            raise CommandError("No matching WebUntis connection found.")

        totals = {"subject_aliases": 0, "teacher_aliases": 0, "changed_lessons": 0}
        for connection in connections:
            try:
                result = apply_reference_mapping(
                    connection,
                    timetable_path=options["timetable"],
                    class_mapping_path=options["class_mappings"],
                )
            except FileNotFoundError as exc:
                raise CommandError(f"Reference file not found: {exc}") from exc
            for key in totals:
                totals[key] += result[key]

        self.stdout.write(
            self.style.SUCCESS(
                "Reference mapping applied: "
                f"{totals['subject_aliases']} subject aliases, "
                f"{totals['teacher_aliases']} teacher aliases, "
                f"{totals['changed_lessons']} lesson rows updated."
            )
        )
