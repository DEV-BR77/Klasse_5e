from django.core.management.base import BaseCommand

from klasse5e.itslearning.models import ItslearningConnection
from klasse5e.itslearning.services import sync_connection


class Command(BaseCommand):
    help = "Synchronisiert alle aktiven itslearning-RSS- und iCal-Feeds."

    def handle(self, *args, **options):
        succeeded = failed = 0
        for connection in ItslearningConnection.objects.filter(active=True):
            if sync_connection(connection):
                succeeded += 1
            else:
                failed += 1
        self.stdout.write(f"itslearning: {succeeded} erfolgreich, {failed} fehlgeschlagen")
