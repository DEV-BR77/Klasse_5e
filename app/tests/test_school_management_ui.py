import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from klasse5e.core.models import School, SchoolClass

HEADER = "id,name,address,address2,zip,city,website,email,school_type,legal_status,provider,fax,phone,director,raw,location\n"


@pytest.mark.django_db
def test_portal_admin_activates_catalog_school_and_adds_a_class(client, admin_user, year):
    school = School.objects.create(
        name="Heinrich-Nordhoff-Gesamtschule",
        search_name="heinrich-nordhoff-gesamtschule",
        postal_code="38440",
        city="Wolfsburg",
        is_active=False,
    )
    client.force_login(admin_user)

    page = client.get(reverse("school-management"), {"q": "Nordhoff"}, secure=True)
    assert page.status_code == 200
    assert b"Heinrich-Nordhoff-Gesamtschule" in page.content

    response = client.post(
        reverse("school-management"),
        {"action": "activate_school", "school_id": school.pk},
        secure=True,
    )
    assert response.status_code == 302
    school.refresh_from_db()
    assert school.is_active is True

    response = client.post(
        reverse("school-management"),
        {
            "action": "add_class",
            "school_id": school.pk,
            "school_year_id": year.pk,
            "grade_level": "7",
            "class_label": "7.1",
            "class_code": "7-1",
        },
        secure=True,
    )
    assert response.status_code == 302
    school_class = SchoolClass.objects.get(school=school, code="7-1")
    assert (school_class.display_name, school_class.grade_level) == ("7.1", "7")


@pytest.mark.django_db
def test_catalog_upload_only_imports_selected_school_as_inactive_candidate(client, admin_user):
    client.force_login(admin_user)
    body = (
        HEADER
        + 'NI-17,Heinrich-Nordhoff-Gesamtschule,Schulweg 1,,38440,Wolfsburg,,,Gesamtschule,,,,,"{}",\n'
    ).encode()
    upload = SimpleUploadedFile("schulen.csv", body, content_type="text/csv")
    preview = client.post(
        reverse("school-catalog-import"),
        {"csv_file": upload, "query": "Nordhoff"},
        secure=True,
    )
    assert preview.status_code == 200
    row = preview.context["rows"][0]

    response = client.post(
        reverse("school-catalog-import"),
        {"action": "import_selected", "selected_row": row["encoded"]},
        secure=True,
    )
    assert response.status_code == 302
    school = School.objects.get(source_id="NI-17")
    assert school.is_active is False
