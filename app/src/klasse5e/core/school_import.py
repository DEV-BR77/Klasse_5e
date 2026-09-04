import codecs
import csv
import hashlib
import io
import json
import re
import unicodedata
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from .models import School

EXPECTED_FIELDS = {
    "id", "name", "address", "address2", "zip", "city", "website", "email",
    "school_type", "legal_status", "provider", "fax", "phone", "director", "raw", "location",
}
MOJIBAKE = ("Ã", "Â", "�")


@dataclass
class ImportStats:
    rows: int = 0
    created: int = 0
    updated: int = 0
    invalid: int = 0
    invalid_location: int = 0
    duplicate_candidates: int = 0
    errors: dict[str, int] = field(default_factory=dict)


def detect_encoding(data):
    if data.startswith(codecs.BOM_UTF8):
        data.decode("utf-8-sig", errors="strict")
        return "utf-8-sig"
    successful = []
    for encoding in ("utf-8", "cp1252"):
        try:
            text = data.decode(encoding, errors="strict")
        except UnicodeDecodeError:
            continue
        if not any(marker in text for marker in MOJIBAKE):
            successful.append(encoding)
    if not successful:
        raise UnicodeError("Die CSV ist nicht fehlerfrei oder enthält Mojibake-Indikatoren.")
    if "utf-8" in successful:
        return "utf-8"
    return successful[0]


def nfc(value, *, limit=2000):
    value = unicodedata.normalize("NFC", str(value or "").strip())
    if "\ufffd" in value or any(marker in value for marker in MOJIBAKE):
        raise UnicodeError("Nicht zulässige Ersatz- oder Mojibake-Zeichen.")
    return value[:limit]


def search_value(value):
    return " ".join(nfc(value).casefold().split())


def parse_location(value):
    value = nfc(value, limit=500)
    if not value:
        return None, None, False
    try:
        if value.startswith("{") or value.startswith("["):
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                lat, lon = parsed.get("lat") or parsed.get("latitude"), parsed.get("lon") or parsed.get("lng") or parsed.get("longitude")
            else:
                lon, lat = parsed[:2]
        else:
            match = re.fullmatch(r"POINT\s*\(\s*([-+0-9.]+)\s+([-+0-9.]+)\s*\)", value, re.I)
            if not match:
                return None, None, False
            lon, lat = match.groups()
        lat, lon = Decimal(str(lat)), Decimal(str(lon))
    except (ValueError, TypeError, InvalidOperation, json.JSONDecodeError):
        return None, None, False
    valid = Decimal("47") <= lat <= Decimal("56") and Decimal("5") <= lon <= Decimal("16")
    return (lat if valid else None), (lon if valid else None), valid


def parse_raw(value):
    value = nfc(value, limit=20_000)
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {"unparsed": True}
    return parsed if isinstance(parsed, dict) else {"value": parsed}


def duplicate_key(row):
    parts = [search_value(row.get(key)) for key in ("name", "zip", "city", "address")]
    return hashlib.sha256("\x1f".join(parts).encode()).hexdigest()[:24] if any(parts) else ""


def import_schools(
    path,
    *,
    dry_run=False,
    batch_size=500,
    source_name="schools.csv",
    cities=None,
    postal_prefixes=None,
):
    data = path.read_bytes()
    encoding = detect_encoding(data)
    text = data.decode(encoding, errors="strict")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if not reader.fieldnames or not EXPECTED_FIELDS.issubset(set(reader.fieldnames)):
        raise ValueError("CSV-Schema stimmt nicht mit dem erwarteten Schulbestand überein.")
    stats = ImportStats()
    seen_duplicates = {}
    rows = []
    city_filter = {search_value(value) for value in (cities or []) if search_value(value)}
    postal_filter = tuple(nfc(value, limit=10) for value in (postal_prefixes or []) if nfc(value, limit=10))
    for _position, source in enumerate(reader, start=2):
        source_city = search_value(source.get("city"))
        source_postal = nfc(source.get("zip"), limit=10)
        if city_filter or postal_filter:
            city_match = source_city in city_filter if city_filter else False
            postal_match = any(source_postal.startswith(prefix) for prefix in postal_filter) if postal_filter else False
            if not city_match and not postal_match:
                continue
        stats.rows += 1
        try:
            source_id = nfc(source.get("id"), limit=80)
            name = nfc(source.get("name"), limit=160)
            if not source_id or not name:
                raise ValueError("required")
            lat, lon, location_valid = parse_location(source.get("location"))
            if source.get("location") and not location_valid:
                stats.invalid_location += 1
            group = duplicate_key(source)
            if group in seen_duplicates and seen_duplicates[group] != source_id:
                stats.duplicate_candidates += 1
            seen_duplicates[group] = source_id
            rows.append((source_id, {
                "source_name": source_name, "source_imported_at": timezone.now(),
                "name": name, "search_name": search_value(name),
                "address": nfc(source.get("address"), limit=200),
                "address2": nfc(source.get("address2"), limit=200),
                "postal_code": nfc(source.get("zip"), limit=10),
                "city": nfc(source.get("city"), limit=120),
                "website": nfc(source.get("website"), limit=200),
                "email": nfc(source.get("email"), limit=254),
                "school_type": nfc(source.get("school_type"), limit=120),
                "legal_status": nfc(source.get("legal_status"), limit=120),
                "provider": nfc(source.get("provider"), limit=200),
                "fax": nfc(source.get("fax"), limit=80), "phone": nfc(source.get("phone"), limit=80),
                "director": nfc(source.get("director"), limit=160), "source_raw": parse_raw(source.get("raw")),
                "latitude": lat, "longitude": lon, "location_valid": location_valid,
                "possible_duplicate_group": group,
            }))
        except (ValueError, UnicodeError) as exc:
            stats.invalid += 1
            key = type(exc).__name__
            stats.errors[key] = stats.errors.get(key, 0) + 1
        if len(rows) >= batch_size:
            _write_batch(rows, stats, dry_run)
            rows.clear()
    _write_batch(rows, stats, dry_run)
    return encoding, stats


def _write_batch(rows, stats, dry_run):
    if dry_run:
        return
    with transaction.atomic():
        for source_id, defaults in rows:
            _, created = School.objects.update_or_create(source_id=source_id, defaults=defaults)
            stats.created += int(created)
            stats.updated += int(not created)
