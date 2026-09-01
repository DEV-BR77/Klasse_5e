from django.core.management.base import BaseCommand

from klasse5e.webuntis.scheduler import run_due_schedules


class Command(BaseCommand):
    help = "Führt ausschließlich fällige, DB-gesperrte Synchronisationspläne aus."

    def handle(self, *args, **options):
        runs = run_due_schedules()
        failed = sum(item.status == "failed" for item in runs)
        self.stdout.write(f"runs={len(runs)} failed={failed}")
