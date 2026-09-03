from django.core.management.base import BaseCommand

from klasse5e.meals.source import sync_plans


class Command(BaseCommand):
    help = "Liest neue oder geänderte Wochen-Speisepläne zurückhaltend ein."

    def handle(self, *args, **options):
        results = sync_plans()
        changed = sum(1 for _plan, imported in results if imported)
        self.stdout.write(self.style.SUCCESS(f"{changed} Speiseplan/-pläne aktualisiert."))
