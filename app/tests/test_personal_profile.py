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

    page = client.get(profile_url, secure=True)
    assert page.status_code == 200
    assert b"peep-63.svg" in page.content
    assert b"data-profile-cropper" in page.content

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
    page = client.get(reverse("personal-profile"), secure=True)
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
