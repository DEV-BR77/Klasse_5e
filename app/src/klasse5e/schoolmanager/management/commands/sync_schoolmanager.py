from django.core.management.base import BaseCommand

from klasse5e.portal_adapters.models import SchoolmanagerConnection
from klasse5e.schoolmanager.sync import sync_connection


class Command(BaseCommand):
    help = "Synchronisiert Schulmanager Online lesend für gespeicherte Kind-Zugänge."

    def add_arguments(self, parser):
        parser.add_argument("--connection", type=int)

    def handle(self, *args, **options):
        connections = SchoolmanagerConnection.objects.all()
        if options.get("connection"):
            connections = connections.filter(pk=options["connection"])
        total = 0
        for connection in connections.iterator():
            try:
                total += sync_connection(connection)
            except Exception as exc:
                self.stderr.write(f"Verbindung {connection.pk} fehlgeschlagen: {type(exc).__name__}")
        self.stdout.write(self.style.SUCCESS(f"{total} neue Schulmanager-Benachrichtigungen angelegt."))
