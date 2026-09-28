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
            "tab": "appearance",
            "save_scope": "appearance",
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

    page = client.get(f"{profile_url}?tab=appearance", secure=True)
    assert page.status_code == 200
    assert b"data-profile-current-preview" in page.content
    assert b"Avatar verwenden" in page.content
    assert b"avatar-designer" in page.content

    response = client.post(
        profile_url,
        {
            "tab": "appearance",
            "save_scope": "appearance",
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
def test_profile_keeps_geocoordinates_without_showing_a_carpool_card(client, guardian):
    client.force_login(guardian)
    response = client.post(
        reverse("personal-profile"),
        {
            "first_name": "Alex",
            "last_name": "Beispiel",
            "contribution_name_mode": "family",
            "profile_image_mode": "avatar",
            "avatar_key": "peep-1",
            "home_latitude": "52.42399149",
            "home_longitude": "10.78622151",
        },
        secure=True,
    )
    assert response.status_code == 302
    guardian.person.refresh_from_db()
    assert str(guardian.person.home_latitude) == "52.423991"
    assert str(guardian.person.home_longitude) == "10.786222"
    page = client.get(reverse("personal-profile"), secure=True)
    assert b"Mein Wohnbereich" not in page.content
    assert b"Wohnbereich gespeichert" not in page.content
    assert b"Dein Profil wurde gespeichert." in page.content
    assert b"data-auto-dismiss" in page.content


@pytest.mark.django_db
def test_profile_save_accepts_localized_optional_map_coordinates(client, guardian):
    client.force_login(guardian)
    response = client.post(
        reverse("personal-profile"),
        {
            "tab": "data", "save_scope": "data", "first_name": "Alex", "last_name": "Beispiel",
            "street": "Musterstraße 1", "home_latitude": "52,42399149", "home_longitude": "10,78622151",
        },
        secure=True,
    )
    assert response.status_code == 302
    guardian.person.refresh_from_db()
    assert guardian.person.street == "Musterstraße 1"
    assert str(guardian.person.home_latitude) == "52.423991"


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
    assert guardian.person.street == "Musterstraße 1"
    assert guardian.person.postal_code == "38440"
    assert guardian.person.city == "Wolfsburg"
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
        {"tab": "notifications", "save_scope": "notifications", "push_chat": "on"},
        secure=True,
    )
    assert response.status_code == 302
    page = client.get(f"{reverse('personal-profile')}?tab=notifications", secure=True)
    assert b"Fahrgemeinschaft" not in page.content


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

    assert response.status_code == 400
    assert b"Deine Angaben wurden noch nicht gespeichert." in response.content
    assert b'value="changed@example.test"' in response.content
    assert b'value="keine Telefonnummer"' in response.content
    guardian.refresh_from_db()
    guardian.person.refresh_from_db()
    assert guardian.email == "guardian@example.test"
    assert guardian.person.phone == ""


@pytest.mark.django_db
def test_profile_save_scopes_do_not_overwrite_each_other(client, guardian):
    client.force_login(guardian)
    guardian.person.avatar_seed = "v2:2:1:3:4:1:2"
    guardian.person.email_visibility = "members"
    guardian.person.phone_visibility = "members"
    guardian.person.save()

    data_response = client.post(
        reverse("personal-profile"),
        {
            "tab": "data", "save_scope": "data", "first_name": "Alex", "last_name": "Beispiel",
            "email": "guardian@example.test", "phone": "05361 123456", "share_email": "yes",
            "share_phone": "yes",
        },
        secure=True,
    )
    assert data_response.status_code == 302
    guardian.person.refresh_from_db()
    assert guardian.person.avatar_seed == "v2:2:1:3:4:1:2"

    appearance_response = client.post(
        reverse("personal-profile"),
        {
            "tab": "appearance", "save_scope": "appearance", "profile_image_mode": "avatar",
            "avatar_key": "peep-1", "avatar_seed": "v2:3:1:3:4:1:2",
        },
        secure=True,
    )
    assert appearance_response.status_code == 302
    guardian.person.refresh_from_db()
    assert guardian.person.email_visibility == "members"
    assert guardian.person.phone_visibility == "members"


@pytest.mark.django_db
def test_profile_persists_a_designed_svg_avatar(client, guardian):
    client.force_login(guardian)

    response = client.post(
        reverse("personal-profile"),
        {
            "tab": "appearance",
            "save_scope": "appearance",
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
@pytest.mark.parametrize("pose,label", [(0, "Stehend"), (1, "Sitzend")])
def test_profile_saves_and_renders_full_body_pose(client, guardian, pose, label):
    client.force_login(guardian)
    seed = f"v3:1:{pose}:0:0:0:0:0"
    response = client.post(
        reverse("personal-profile"),
        {"tab": "appearance", "save_scope": "appearance", "profile_image_mode": "avatar",
         "avatar_seed": seed},
        secure=True,
    )
    assert response.status_code == 302
    guardian.person.refresh_from_db()
    assert guardian.person.avatar_seed == seed
    page = client.get(f"{reverse('personal-profile')}?tab=appearance", secure=True)
    assert page.status_code == 200
    assert label in page.content.decode()
    assert f"pose/{'standing' if pose == 0 else 'sitting'}" in page.content.decode()


@pytest.mark.django_db
def test_profile_rejects_invalid_avatar_without_a_server_error(client, guardian):
    client.force_login(guardian)
    response = client.post(
        reverse("personal-profile"),
        {
            "tab": "appearance",
            "save_scope": "appearance",
            "first_name": "Alex", "last_name": "Beispiel", "contribution_name_mode": "family",
            "profile_image_mode": "avatar", "avatar_seed": "v2:99:99:99:99:99:99",
        },
        secure=True,
    )
    assert response.status_code == 400


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
