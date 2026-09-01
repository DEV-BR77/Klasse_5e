import codecs
from pathlib import Path

import pytest
from django.core.exceptions import ValidationError

from klasse5e.core.models import School
from klasse5e.core.school_domains import propose_class_hostname, validate_class_hostname
from klasse5e.core.school_import import detect_encoding, import_schools, search_value

HEADER = "id,name,address,address2,zip,city,website,email,school_type,legal_status,provider,fax,phone,director,raw,location\n"


def csv_bytes(encoding="utf-8"):
    row = '1,Müller-Schule,Straße 1,,01234,Köln,,,Gymnasium,öffentlich,,,,,"{}","POINT (7.1 50.7)"\n'
    return (HEADER + row).encode(encoding)


def test_encoding_and_unicode_are_lossless():
    assert detect_encoding(csv_bytes()) == "utf-8"
    assert detect_encoding(codecs.BOM_UTF8 + csv_bytes()) == "utf-8-sig"
    assert detect_encoding(csv_bytes("cp1252")) == "cp1252"
    assert search_value("Gießen Straße") == "giessen strasse"
    assert search_value("GROẞ-GERAU") == "gross-gerau"


def test_mojibake_is_rejected():
    with pytest.raises(UnicodeError):
        detect_encoding((HEADER + "1,MÃ¼ller,,,,,,,,,,,,,,,\n").encode())


@pytest.mark.django_db
def test_import_is_idempotent_preserves_zero_zip_and_updates(tmp_path: Path):
    path = tmp_path / "schools.csv"
    path.write_bytes(csv_bytes())
    encoding, first = import_schools(path, batch_size=10)
    _, second = import_schools(path, batch_size=10)
    school = School.objects.get(source_id="1")
    assert encoding == "utf-8"
    assert (first.created, second.updated, School.objects.filter(source_id__isnull=False).count()) == (1, 1, 1)
    assert school.name == "Müller-Schule"
    assert school.postal_code == "01234"
    assert school.city == "Köln"
    assert school.location_valid


def test_hostname_rules():
    assert propose_class_hostname("5.1", "THG") == "5-1-thg.klassid.de"
    assert validate_class_hostname("5e.klassid.de", reserved_exception=True)
    with pytest.raises(ValidationError):
        validate_class_hostname("admin.klassid.de")
