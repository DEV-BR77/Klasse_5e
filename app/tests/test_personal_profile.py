from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from klasse5e.core.models import Person


def _profile_photo():
    image = Image.new("RGB", (8, 8), color="#7058d8")
    payload = BytesIO()
    image.save(payload, format="PNG")
    return SimpleUploadedFile("profil.png", payload.getvalue(), content_type="image/png")


@pytest.mark.django_db
def test_owner_can_preview_a_saved_profile_photo_and_switch_to_an_avatar(client, guardian):
    client.force_login(guardian)
    profile_url = reverse("personal-profile")
    response = client.post(
        profile_url,
        {
            "first_name": "Alex",
            "last_name": "Beispiel",
            "contribution_name_mode": "family",
            "profile_image_mode": "photo",
            "avatar_key": "peep-63",
            "profile_photo": _profile_photo(),
        },
        secure=True,
    )
    assert response.status_code == 302

    guardian.person.refresh_from_db()
    assert guardian.person.profile_photo
    assert guardian.person.profile_image_mode == Person.ProfileImageMode.PHOTO
    assert guardian.person.avatar_key == "peep-63"

    image = client.get(reverse("profile-photo", args=[guardian.person.pk]), secure=True)
    assert image.status_code == 200
    assert image["Content-Type"] == "image/webp"
    # On Windows the test client can otherwise retain the file handle while
    # the following request removes the just-used profile image.
    image.close()

    page = client.get(f"{profile_url}?tab=appearance", secure=True)
    assert page.status_code == 200
    assert b"data-profile-current-preview" in page.content
    assert b"Avatar verwenden" in page.content
    assert b"avatar-designer" in page.content

    response = client.post(
        profile_url,
        {
            "first_name": "Alex",
            "last_name": "Beispiel",
            "contribution_name_mode": "family",
            "profile_image_mode": "avatar",
            "avatar_key": "peep-94",
            "remove_profile_photo": "yes",
        },
        secure=True,
    )
    assert response.status_code == 302
    guardian.person.refresh_from_db()
    assert not guardian.person.profile_photo
    assert guardian.person.profile_image_mode == Person.ProfileImageMode.AVATAR
    assert guardian.person.avatar_key == "peep-94"


@pytest.mark.django_db
def test_profile_home_area_persists_one_current_location(client, guardian):
    client.force_login(guardian)
    response = client.post(
        reverse("personal-profile"),
        {
            "first_name": "Alex",
            "last_name": "Beispiel",
            "contribution_name_mode": "family",
            "profile_image_mode": "avatar",
            "avatar_key": "peep-1",
            "home_latitude": "52.423991",
            "home_longitude": "10.786221",
        },
        secure=True,
    )
    assert response.status_code == 302
    guardian.person.refresh_from_db()
    assert str(guardian.person.home_latitude) == "52.423991"
    assert str(guardian.person.home_longitude) == "10.786221"
    page = client.get(reverse("personal-profile"), secure=True)
    assert b"Mein Wohnbereich" in page.content
    assert b"Wohnbereich gespeichert" in page.content


@pytest.mark.django_db
def test_profile_stores_contact_visibility_and_notification_preferences(client, guardian):
    client.force_login(guardian)
    response = client.post(
        reverse("personal-profile"),
        {
            "tab": "data", "save_scope": "data", "first_name": "Alex", "last_name": "Beispiel",
            "street": "Musterstraße 1", "postal_code": "38440", "city": "Wolfsburg",
            "email": "new-address@example.test", "phone": "05361 123456",
            "share_email": "yes", "share_phone": "yes",
            "share_address": "yes",
        },
        secure=True,
    )
    assert response.status_code == 302
    guardian.refresh_from_db()
    guardian.person.refresh_from_db()
    assert guardian.email == "new-address@example.test"
    assert guardian.person.phone == "+495361123456"
    assert guardian.person.email_visibility == "members"
    assert guardian.person.phone_visibility == "members"
    assert all(
        guardian.person.field_visibility[field]
        for field in ("street", "postal_code", "city")
    )
    page = client.get(f"{reverse('personal-profile')}?tab=data", secure=True)
    assert page.content.decode().count('class="sharing-toggle"') == 3
    response = client.post(
        reverse("personal-profile"),
        {"tab": "notifications", "save_scope": "notifications", "push_chat": "on", "inapp_carpool": "on"},
        secure=True,
    )
    assert response.status_code == 302
    page = client.get(f"{reverse('personal-profile')}?tab=notifications", secure=True)
    assert b"Fahrgemeinschaft" in page.content


@pytest.mark.django_db
def test_profile_rejects_invalid_contact_data_atomically(client, guardian):
    client.force_login(guardian)
    response = client.post(
        reverse("personal-profile"),
        {
            "tab": "data",
            "save_scope": "data",
            "first_name": "Alex",
            "last_name": "Beispiel",
            "email": "changed@example.test",
            "phone": "keine Telefonnummer",
        },
        secure=True,
    )

    assert response.status_code == 302
    guardian.refresh_from_db()
    assert guardian.email == "guardian@example.test"
    assert guardian.person.phone == ""


@pytest.mark.django_db
def test_profile_persists_a_designed_svg_avatar(client, guardian):
    client.force_login(guardian)

    response = client.post(
        reverse("personal-profile"),
        {
            "first_name": "Alex", "last_name": "Beispiel", "contribution_name_mode": "family",
            "profile_image_mode": "avatar", "avatar_key": "peep-1",
            "avatar_seed": "v2:2:1:3:4:1:2",
        },
        secure=True,
    )

    assert response.status_code == 302
    guardian.person.refresh_from_db()
    assert guardian.person.avatar_seed == "v2:2:1:3:4:1:2"
    page = client.get(f"{reverse('personal-profile')}?tab=appearance", secure=True)
    assert b"Avatar-Designer" in page.content


@pytest.mark.django_db
def test_profile_rejects_invalid_avatar_without_a_server_error(client, guardian):
    client.force_login(guardian)
    response = client.post(
        reverse("personal-profile"),
        {
            "first_name": "Alex", "last_name": "Beispiel", "contribution_name_mode": "family",
            "profile_image_mode": "avatar", "avatar_seed": "v2:99:99:99:99:99:99",
        },
        secure=True,
    )
    assert response.status_code == 302


@pytest.mark.django_db
def test_app_installation_help_has_separate_android_and_ios_guides(client, guardian):
    client.force_login(guardian)

    page = client.get(f"{reverse('personal-profile')}?tab=app", secure=True)

    assert page.status_code == 200
    content = page.content.decode()
    assert "KlassID als App installieren" in content
    assert "ständigen Zugriff" in content
    assert "Android" in content
    assert "iOS-Geräte" in content
    assert "Zum Startbildschirm hinzufügen" in content
    assert "Zum Home-Bildschirm" in content
