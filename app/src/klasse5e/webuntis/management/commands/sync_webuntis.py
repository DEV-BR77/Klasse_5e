from django.core.management.base import BaseCommand

from klasse5e.webuntis.models import SyncRun, SyncSchedule, WebUntisConnection
from klasse5e.webuntis.sync import SyncThrottled, run_connection


class Command(BaseCommand):
    help = "Führt einen kontrollierten WebUntis-Synchronisationslauf aus."

    def add_arguments(self, parser):
        parser.add_argument("--automatic", action="store_true")

    def handle(self, *args, **options):
        schedule = SyncSchedule.current()
        if options["automatic"] and not schedule.enabled:
            self.stdout.write("Automatische WebUntis-Synchronisierung ist deaktiviert.")
            return
        for connection in WebUntisConnection.objects.all().iterator():
            try:
                run = run_connection(
                    connection,
                    trigger=SyncRun.Trigger.AUTOMATIC
                    if options["automatic"]
                    else SyncRun.Trigger.MANUAL,
                )
                self.stdout.write(f"Verbindung {connection.pk}: {run.status}")
            except SyncThrottled:
                self.stdout.write(f"Verbindung {connection.pk}: throttled")
