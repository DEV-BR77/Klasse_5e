import csv
from io import StringIO

import pytest

from klasse5e.core.models import School, SchoolClass, SchoolYear
from klasse5e.core.school_setup_transfer import FIELDS, apply_rows, export_csv, parse_csv
from klasse5e.portal_adapters.models import PortalAdapter, PortalAdapterModule


def _row(**values):
    row = {field: "" for field in FIELDS}
    row.update(
        {
            "school_slug": "test-gymnasium",
            "school_name": "Test-Gymnasium",
            "school_postal_code": "38440",
            "school_city": "Wolfsburg",
            "school_active": "ja",
            "school_year_label": "2026/27",
            "school_year_starts_on": "2026-08-01",
            "school_year_ends_on": "2027-07-31",
            "school_year_active": "ja",
            "class_code": "5.1",
            "class_name": "Klasse 5.1",
            "class_display_name": "5.1",
            "class_grade_level": "5",
            "class_status": "active",
            "adapter_provider": "webuntis",
            "adapter_name": "WebUntis Test",
            "adapter_enabled": "ja",
            "adapter_requires_child_credentials": "ja",
            "module_key": "timetable",
            "module_label": "Stundenplan",
            "module_enabled": "ja",
            "module_requires_child_credentials": "ja",
            "module_status": "ready",
        }
    )
    row.update(values)
    return row


@pytest.mark.django_db
def test_school_setup_import_creates_classes_adapters_and_class_scoped_module():
    first = _row(module_available_classes="2026/27:5.1")
    second = _row(
        class_code="5.2",
        class_name="Klasse 5.2",
        class_display_name="5.2",
        adapter_provider="",
        adapter_name="",
        module_key="",
        module_label="",
        module_enabled="",
        module_requires_child_credentials="",
        module_status="",
    )

    stats = apply_rows([first, second])

    school = School.objects.get(slug="test-gymnasium")
    school_year = SchoolYear.objects.get(label="2026/27")
    assert SchoolClass.objects.filter(school=school, school_year=school_year).count() == 2
    module = PortalAdapterModule.objects.get(adapter__school=school, key="timetable")
    assert list(module.available_to_classes.values_list("code", flat=True)) == ["5.1"]
    assert stats.schools_created == 1
    assert stats.adapters_created == 1


@pytest.mark.django_db
def test_school_setup_export_is_a_valid_idempotent_import_template():
    school = School.objects.create(name="Exportschule", slug="exportschule", postal_code="38518", city="Gifhorn")
    school_year = SchoolYear.objects.create(
        label="2026/27", starts_on="2026-08-01", ends_on="2027-07-31", is_active=True
    )
    school_class = SchoolClass.objects.create(
        school=school, school_year=school_year, code="5.1", name="Klasse 5.1", display_name="5.1"
    )
    adapter = PortalAdapter.objects.create(school=school, provider="itslearning", name="itslearning")
    module = PortalAdapterModule.objects.create(adapter=adapter, key="calendar", label="Kalender")
    module.available_to_classes.add(school_class)

    rows = parse_csv(export_csv().encode("utf-8"))
    apply_rows(rows)

    assert School.objects.filter(slug="exportschule").count() == 1
    assert SchoolClass.objects.filter(school=school, school_year=school_year, code="5.1").count() == 1
    assert PortalAdapter.objects.filter(school=school, provider="itslearning", name="itslearning").count() == 1


def test_school_setup_parser_rejects_foreign_or_malformed_csv_contract():
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=("school_name",))
    writer.writeheader()
    writer.writerow({"school_name": "Keine Vorlage"})

    with pytest.raises(ValueError, match="Spalten"):
        parse_csv(output.getvalue().encode("utf-8"))
