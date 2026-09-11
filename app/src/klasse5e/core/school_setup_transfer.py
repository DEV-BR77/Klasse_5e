"""Safe, Excel-compatible transfer of school setup data.

The transfer deliberately excludes people, invitations, family data and all
credentials.  It is a small, reviewable administrative data contract for
schools, classes and the already reviewed portal adapters only.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from io import StringIO

from django.db import transaction
from django.utils.text import slugify

from klasse5e.portal_adapters.models import PortalAdapter, PortalAdapterModule

from .models import School, SchoolClass, SchoolYear

FIELDS = (
    "school_slug",
    "school_name",
    "school_short_name",
    "school_address",
    "school_postal_code",
    "school_city",
    "school_website",
    "school_active",
    "school_year_label",
    "school_year_starts_on",
    "school_year_ends_on",
    "school_year_active",
    "class_code",
    "class_name",
    "class_display_name",
    "class_grade_level",
    "class_status",
    "class_valid_from",
    "class_valid_until",
    "adapter_provider",
    "adapter_name",
    "adapter_base_url",
    "adapter_project_identifier",
    "adapter_institution_identifier",
    "adapter_school_number",
    "adapter_enabled",
    "adapter_requires_child_credentials",
    "adapter_configuration_note",
    "module_key",
    "module_label",
    "module_description",
    "module_enabled",
    "module_requires_child_credentials",
    "module_status",
    "module_configuration_note",
    "module_available_classes",
)

_TRUE = {"1", "true", "yes", "ja", "y"}
_FALSE = {"0", "false", "no", "nein", "n"}
_PROVIDERS = {choice for choice, _label in PortalAdapter.Provider.choices}
_MODULE_STATUSES = {choice for choice, _label in PortalAdapterModule.Status.choices}


@dataclass(frozen=True)
class TransferStats:
    schools_created: int = 0
    schools_updated: int = 0
    years_created: int = 0
    years_updated: int = 0
    classes_created: int = 0
    classes_updated: int = 0
    adapters_created: int = 0
    adapters_updated: int = 0
    modules_created: int = 0
    modules_updated: int = 0


def export_rows() -> list[dict[str, str]]:
    """Return one deterministic row per adapter module (or class if none)."""

    rows: list[dict[str, str]] = []
    schools = School.objects.prefetch_related(
        "classes__school_year", "portal_adapters__modules__available_to_classes"
    ).order_by("slug", "name")
    for school in schools:
        base = _school_values(school)
        classes = list(school.classes.select_related("school_year").order_by("school_year__label", "code"))
        adapters = list(school.portal_adapters.prefetch_related("modules__available_to_classes").order_by("provider", "name"))
        for school_class in classes:
            rows.append({**base, **_class_values(school_class)})
        if not adapters:
            continue
        for adapter in adapters:
            modules = list(adapter.modules.all().order_by("key"))
            if not modules:
                rows.append({**base, **_adapter_values(adapter)})
                continue
            for module in modules:
                rows.append({**base, **_adapter_values(adapter), **_module_values(module)})
    return rows or [{field: "" for field in FIELDS}]


def export_csv() -> str:
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(export_rows())
    return output.getvalue()


def parse_csv(data: bytes) -> list[dict[str, str]]:
    if len(data) > 5 * 1024 * 1024:
        raise ValueError("Die Importdatei darf höchstens 5 MB groß sein.")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Bitte speichere die Excel-Datei als UTF-8-CSV.") from exc
    reader = csv.DictReader(StringIO(text, newline=""))
    if not reader.fieldnames or set(FIELDS) - set(reader.fieldnames):
        raise ValueError("Die Spalten stimmen nicht mit dem KlassID-Export überein.")
    rows = [{field: str(row.get(field) or "").strip() for field in FIELDS} for row in reader]
    rows = [row for row in rows if any(row.values())]
    if not rows:
        raise ValueError("Die Importdatei enthält keine Datenzeile.")
    if len(rows) > 1500:
        raise ValueError("Bitte höchstens 1.500 Zeilen pro Import verwenden.")
    validate_rows(rows)
    return rows


def validate_rows(rows: list[dict[str, str]]) -> None:
    errors: list[str] = []
    for number, row in enumerate(rows, start=2):
        prefix = f"Zeile {number}:"
        if not row["school_slug"] or not row["school_name"]:
            errors.append(f"{prefix} school_slug und school_name sind erforderlich.")
        if row["school_slug"] and slugify(row["school_slug"]) != row["school_slug"]:
            errors.append(f"{prefix} school_slug muss eine URL-taugliche Kennung sein.")
        _validate_boolean(row, "school_active", prefix, errors)
        has_class = any(row[field] for field in ("class_code", "class_name", "school_year_label"))
        if has_class:
            if not all(row[field] for field in ("school_year_label", "school_year_starts_on", "school_year_ends_on", "class_code", "class_name")):
                errors.append(f"{prefix} Klassen brauchen Schuljahr, Start, Ende, class_code und class_name.")
            _validate_date(row, "school_year_starts_on", prefix, errors)
            _validate_date(row, "school_year_ends_on", prefix, errors)
            _validate_date(row, "class_valid_from", prefix, errors, optional=True)
            _validate_date(row, "class_valid_until", prefix, errors, optional=True)
            _validate_boolean(row, "school_year_active", prefix, errors)
        has_adapter = any(row[field] for field in ("adapter_provider", "adapter_name"))
        if has_adapter:
            if row["adapter_provider"] not in _PROVIDERS or not row["adapter_name"]:
                errors.append(f"{prefix} Adapter braucht einen bekannten adapter_provider und adapter_name.")
            _validate_boolean(row, "adapter_enabled", prefix, errors)
            _validate_boolean(row, "adapter_requires_child_credentials", prefix, errors)
        has_module = any(row[field] for field in ("module_key", "module_label"))
        if has_module:
            if not has_adapter or not row["module_key"] or not row["module_label"]:
                errors.append(f"{prefix} Modul braucht einen Adapter sowie module_key und module_label.")
            if row["module_status"] and row["module_status"] not in _MODULE_STATUSES:
                errors.append(f"{prefix} module_status ist ungültig.")
            _validate_boolean(row, "module_enabled", prefix, errors)
            _validate_boolean(row, "module_requires_child_credentials", prefix, errors)
    if errors:
        raise ValueError(" ".join(errors[:12]))


def apply_rows(rows: list[dict[str, str]]) -> TransferStats:
    """Apply a previously validated transfer atomically and idempotently."""

    validate_rows(rows)
    counts = {field: 0 for field in TransferStats.__dataclass_fields__}
    classes_by_reference: dict[tuple[str, str, str], SchoolClass] = {}
    with transaction.atomic():
        for row in rows:
            school = School.objects.filter(slug=row["school_slug"]).first()
            created = school is None
            if school is None:
                # Older manually created schools may not have a slug yet.  An
                # exact name/postcode/city match is safe enough to backfill one
                # during their first export/import cycle; ambiguous matches do
                # not get silently merged.
                matches = School.objects.filter(
                    name=row["school_name"],
                    postal_code=row["school_postal_code"],
                    city=row["school_city"],
                )
                if matches.count() == 1:
                    school = matches.get()
                    created = False
                else:
                    school = School(slug=row["school_slug"], name=row["school_name"])
            counts["schools_created" if created else "schools_updated"] += 1
            _update_school(school, row)
            school.save()

            if row["school_year_label"]:
                year, year_created = SchoolYear.objects.get_or_create(
                    label=row["school_year_label"],
                    defaults={
                        "starts_on": _date(row["school_year_starts_on"]),
                        "ends_on": _date(row["school_year_ends_on"]),
                        "is_active": _boolean(row["school_year_active"], default=False),
                    },
                )
                counts["years_created" if year_created else "years_updated"] += 1
                year.starts_on = _date(row["school_year_starts_on"])
                year.ends_on = _date(row["school_year_ends_on"])
                year.is_active = _boolean(row["school_year_active"], default=False)
                year.full_clean()
                year.save()
                school_class, class_created = SchoolClass.objects.get_or_create(
                    school=school,
                    school_year=year,
                    code=row["class_code"],
                    defaults={"name": row["class_name"]},
                )
                counts["classes_created" if class_created else "classes_updated"] += 1
                _update_class(school_class, row)
                school_class.save()
                classes_by_reference[(school.slug, year.label, school_class.code)] = school_class

        # Adapter modules may refer to classes listed later in the spreadsheet.
        # Resolve every class first, then apply integrations in a second pass.
        for row in rows:
            school = School.objects.get(slug=row["school_slug"])
            if row["adapter_provider"]:
                adapter, adapter_created = PortalAdapter.objects.get_or_create(
                    school=school,
                    provider=row["adapter_provider"],
                    name=row["adapter_name"],
                )
                counts["adapters_created" if adapter_created else "adapters_updated"] += 1
                _update_adapter(adapter, row)
                adapter.full_clean()
                adapter.save()
                if row["module_key"]:
                    module, module_created = PortalAdapterModule.objects.get_or_create(
                        adapter=adapter, key=row["module_key"]
                    )
                    counts["modules_created" if module_created else "modules_updated"] += 1
                    _update_module(module, row)
                    module.full_clean()
                    module.save()
                    _set_module_classes(module, school, row, classes_by_reference)
    return TransferStats(**counts)


def _set_module_classes(module, school, row, references):
    raw = row["module_available_classes"].strip()
    if not raw or raw == "*":
        module.available_to_classes.clear()
        return
    selected = []
    for value in raw.split("|"):
        try:
            year_label, code = (part.strip() for part in value.split(":", 1))
        except ValueError as exc:
            raise ValueError("module_available_classes erwartet Schuljahr:Klassen-Code, getrennt mit |.") from exc
        school_class = references.get((school.slug, year_label, code)) or SchoolClass.objects.filter(
            school=school, school_year__label=year_label, code=code
        ).first()
        if school_class is None:
            raise ValueError(f"Modulklasse {year_label}:{code} wurde nicht gefunden.")
        selected.append(school_class)
    module.available_to_classes.set(selected)


def _school_values(school):
    return {
        "school_slug": school.slug or slugify(f"{school.name}-{school.postal_code}-{school.city}"),
        "school_name": school.name,
        "school_short_name": school.short_name,
        "school_address": school.address,
        "school_postal_code": school.postal_code,
        "school_city": school.city,
        "school_website": school.website,
        "school_active": _yes_no(school.is_active),
    }


def _class_values(school_class):
    if school_class is None:
        return {}
    return {
        "school_year_label": school_class.school_year.label,
        "school_year_starts_on": school_class.school_year.starts_on.isoformat(),
        "school_year_ends_on": school_class.school_year.ends_on.isoformat(),
        "school_year_active": _yes_no(school_class.school_year.is_active),
        "class_code": school_class.code,
        "class_name": school_class.name,
        "class_display_name": school_class.display_name,
        "class_grade_level": school_class.grade_level,
        "class_status": school_class.status,
        "class_valid_from": school_class.valid_from.isoformat() if school_class.valid_from else "",
        "class_valid_until": school_class.valid_until.isoformat() if school_class.valid_until else "",
    }


def _adapter_values(adapter):
    return {
        "adapter_provider": adapter.provider,
        "adapter_name": adapter.name,
        "adapter_base_url": adapter.base_url,
        "adapter_project_identifier": adapter.project_identifier,
        "adapter_institution_identifier": adapter.institution_identifier,
        "adapter_school_number": adapter.school_number,
        "adapter_enabled": _yes_no(adapter.is_enabled),
        "adapter_requires_child_credentials": _yes_no(adapter.requires_child_credentials),
        "adapter_configuration_note": adapter.configuration_note,
    }


def _module_values(module):
    values = [f"{item.school_year.label}:{item.code}" for item in module.available_to_classes.all().select_related("school_year").order_by("school_year__label", "code")]
    return {
        "module_key": module.key,
        "module_label": module.label,
        "module_description": module.description,
        "module_enabled": _yes_no(module.is_enabled),
        "module_requires_child_credentials": _yes_no(module.requires_child_credentials),
        "module_status": module.status,
        "module_configuration_note": module.configuration_note,
        "module_available_classes": "|".join(values),
    }


def _update_school(school, row):
    if not school.slug:
        school.slug = row["school_slug"]
    school.name = row["school_name"]
    school.short_name = row["school_short_name"]
    school.address = row["school_address"]
    school.postal_code = row["school_postal_code"]
    school.city = row["school_city"]
    school.website = row["school_website"]
    school.is_active = _boolean(row["school_active"], default=True)


def _update_class(school_class, row):
    school_class.name = row["class_name"]
    school_class.display_name = row["class_display_name"]
    school_class.grade_level = row["class_grade_level"]
    school_class.status = row["class_status"] or "active"
    school_class.valid_from = _date(row["class_valid_from"]) if row["class_valid_from"] else None
    school_class.valid_until = _date(row["class_valid_until"]) if row["class_valid_until"] else None


def _update_adapter(adapter, row):
    adapter.base_url = row["adapter_base_url"]
    adapter.project_identifier = row["adapter_project_identifier"]
    adapter.institution_identifier = row["adapter_institution_identifier"]
    adapter.school_number = row["adapter_school_number"]
    adapter.is_enabled = _boolean(row["adapter_enabled"], default=False)
    adapter.requires_child_credentials = _boolean(row["adapter_requires_child_credentials"], default=False)
    adapter.configuration_note = row["adapter_configuration_note"]


def _update_module(module, row):
    module.label = row["module_label"]
    module.description = row["module_description"]
    module.is_enabled = _boolean(row["module_enabled"], default=False)
    module.requires_child_credentials = _boolean(row["module_requires_child_credentials"], default=False)
    module.status = row["module_status"] or PortalAdapterModule.Status.NOT_CONFIGURED
    module.configuration_note = row["module_configuration_note"]


def _validate_boolean(row, field, prefix, errors):
    value = row[field].casefold()
    if value and value not in _TRUE | _FALSE:
        errors.append(f"{prefix} {field} erwartet ja oder nein.")


def _validate_date(row, field, prefix, errors, optional=False):
    if not row[field] and optional:
        return
    try:
        _date(row[field])
    except ValueError:
        errors.append(f"{prefix} {field} erwartet YYYY-MM-DD.")


def _boolean(value, *, default):
    if not value:
        return default
    return value.casefold() in _TRUE


def _date(value):
    return date.fromisoformat(value)


def _yes_no(value):
    return "ja" if value else "nein"
