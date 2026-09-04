import pytest
from allauth.mfa.models import Authenticator
from allauth.mfa.utils import is_mfa_enabled
from django.test import override_settings

from klasse5e.core.models import FamilyAccessCode


@pytest.mark.django_db
def test_portal_admin_menu_exposes_school_class_and_family_workflows(
    client, admin_user, school_class
):
    client.force_login(admin_user)

    response = client.get("/mehr/", secure=True)

    assert response.status_code == 200
    content = response.content.decode()
    assert "Portalverwaltung" in content
    assert "/admin/core/school/" in content
    assert "/admin/core/schoolclass/" in content
    assert "/verwaltung/familien-einladungen/" in content


@pytest.mark.django_db
def test_admin_can_generate_named_family_invitation_pdf(client, admin_user, school_class):
    client.force_login(admin_user)

    response = client.post(
        "/verwaltung/familien-einladungen/",
        {
            "school_class": school_class.pk,
            "count": 2,
            "family_names": "Familie Muster\nFamilie Beispiel",
        },
        secure=True,
    )

    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert "attachment" in response["Content-Disposition"]
    assert b"%PDF" in b"".join(response.streaming_content)[:8]
    assert list(
        FamilyAccessCode.objects.order_by("serial_number").values_list(
            "intended_family_name", flat=True
        )
    ) == ["Familie Muster", "Familie Beispiel"]


@pytest.mark.django_db
def test_family_invitation_workflow_is_hidden_from_guardians(client, guardian):
    client.force_login(guardian)
    assert client.get("/verwaltung/familien-einladungen/", secure=True).status_code == 404


@pytest.mark.django_db
@override_settings(TEMPORARY_ADMIN_MFA_BYPASS=True)
def test_temporary_mfa_bypass_only_applies_to_top_level_admin(admin_user, guardian):
    Authenticator.objects.create(
        user=guardian,
        type=Authenticator.Type.TOTP,
        data={"secret": "synthetic-test-only"},
    )
    assert is_mfa_enabled(admin_user) is False
    assert is_mfa_enabled(guardian) is True
