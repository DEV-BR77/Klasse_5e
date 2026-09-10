import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from klasse5e.portal_adapters.models import PortalAdapter
from klasse5e.webuntis.extra_models import (
    WebUntisSubjectMapping,
    WebUntisTeacherMapping,
)


def _import_csv(path_value, model, *, adapter):
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
            label = (row.get("label") or "").strip().rstrip(",").strip()
            if not code or not label:
                continue
            model.objects.update_or_create(adapter=adapter, code=code, defaults={"label": label})
            count += 1
    return count


class Command(BaseCommand):
    help = "Imports local teacher and subject mappings from code,label CSV files."

    def add_arguments(self, parser):
        parser.add_argument("--teachers", required=True)
        parser.add_argument("--subjects", required=True)
        parser.add_argument("--adapter-id", type=int, required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            adapter = PortalAdapter.objects.get(
                pk=options["adapter_id"], provider=PortalAdapter.Provider.WEBUNTIS
            )
        except PortalAdapter.DoesNotExist as exc:
            raise CommandError("Die angegebene WebUntis-Integration existiert nicht.") from exc
        teachers = _import_csv(options["teachers"], WebUntisTeacherMapping, adapter=adapter)
        subjects = _import_csv(options["subjects"], WebUntisSubjectMapping, adapter=adapter)
        self.stdout.write(f"Imported {teachers} teacher and {subjects} subject mappings.")
