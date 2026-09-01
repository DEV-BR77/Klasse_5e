import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from klasse5e.webuntis.extra_models import (
    WebUntisSubjectMapping,
    WebUntisTeacherMapping,
)


def _import_csv(path_value, model):
    path = Path(path_value).resolve()
    if not path.is_file():
        raise CommandError(f"Mapping file not found: {path.name}")
    count = 0
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not {"code", "label"}.issubset(reader.fieldnames):
            raise CommandError(f"{path.name} must contain code,label headers.")
        for row in reader:
            code = (row.get("code") or "").strip()
            label = (row.get("label") or "").strip()
            if not code or not label:
                continue
            model.objects.update_or_create(code=code, defaults={"label": label})
            count += 1
    return count


class Command(BaseCommand):
    help = "Imports local teacher and subject mappings from code,label CSV files."

    def add_arguments(self, parser):
        parser.add_argument("--teachers", required=True)
        parser.add_argument("--subjects", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        teachers = _import_csv(options["teachers"], WebUntisTeacherMapping)
        subjects = _import_csv(options["subjects"], WebUntisSubjectMapping)
        self.stdout.write(f"Imported {teachers} teacher and {subjects} subject mappings.")
