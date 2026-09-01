from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from klasse5e.core.school_import import import_schools


class Command(BaseCommand):
    help = "Importiert den lokalen Schulbestand idempotent und ohne Inhaltsausgabe."

    def add_arguments(self, parser):
        parser.add_argument("path", type=Path)
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--batch-size", type=int, default=500)

    def handle(self, *args, **options):
        path = options["path"]
        if not path.is_file():
            raise CommandError("Die lokale schools.csv wurde nicht gefunden.")
        size = options["batch_size"]
        if not 10 <= size <= 5000:
            raise CommandError("Batchgröße muss zwischen 10 und 5000 liegen.")
        try:
            encoding, stats = import_schools(path, dry_run=options["dry_run"], batch_size=size)
        except (UnicodeError, ValueError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(
            f"encoding={encoding} rows={stats.rows} created={stats.created} updated={stats.updated} "
            f"invalid={stats.invalid} invalid_location={stats.invalid_location} "
            f"duplicate_candidates={stats.duplicate_candidates}"
        )
