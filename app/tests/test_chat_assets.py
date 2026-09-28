import pytest
from io import BytesIO
from PIL import Image
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile

from klasse5e.chat.models import ChatAsset, ChatMessage, ChatRoom, ChatRoomMember
from klasse5e.chat.services import may_moderate, require_room_access
from klasse5e.core.models import ClassMembership, Person, UserAccount


@pytest.mark.django_db
def test_portal_admin_can_manage_central_chat_assets(client, admin_user, school_class):
    client.force_login(admin_user)

    page = client.get("/verwaltung/chat-elemente/", secure=True)
    assert page.status_code == 200
    assert "Emojis &amp; Sticker" in page.content.decode()

    response = client.post(
        "/verwaltung/chat-elemente/",
        {
            "action": "save",
            "kind": "sticker",
            "label": "Lernheld",
            "value": "sticker-lernheld",
            "is_active": "on",
            "sort_order": "3",
        },
        secure=True,
    )
    assert response.status_code == 302
    asset = ChatAsset.objects.get(label="Lernheld")
    assert asset.value == "sticker-lernheld"

    ChatRoom.objects.create(
        school_class=school_class,
        school_year=school_class.school_year,
        title="Asset-Test",
    )
    chat = client.get("/chat/", secure=True)
    assert chat.status_code == 200


@pytest.mark.django_db
def test_chat_asset_management_is_hidden_from_guardians(client, guardian):
    client.force_login(guardian)
    assert client.get("/verwaltung/chat-elemente/", secure=True).status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize("invalid", [{"sort_order": "-1"}, {"sort_order": "oops"}, {"label": "x" * 81}, {"value": "x" * 241}, {"kind": "unknown"}])
def test_invalid_chat_asset_keeps_input_and_database_unchanged(client, admin_user, invalid):
    client.force_login(admin_user)
    asset = ChatAsset.objects.create(kind="emoji", label="Original", value="👍")
    data = dict(action="save", asset_id=asset.pk, kind="emoji", label="Entwurf", value="🙂", sort_order="2", is_active="on")
    data.update(invalid)
    response = client.post("/verwaltung/chat-elemente/", data, secure=True)
    assert response.status_code == 400
    assert response.context["asset_form"].is_bound
    assert response.context["asset_form"].data["label"] == data["label"]
    asset.refresh_from_db()
    assert asset.label == "Original"
    assert asset.value == "👍"


@pytest.mark.django_db
def test_duplicate_chat_asset_is_validation_error_and_can_be_corrected(client, admin_user):
    client.force_login(admin_user)
    ChatAsset.objects.create(kind="emoji", label="Doppelt", value="👍")
    data = dict(action="save", kind="emoji", label="Doppelt", value="🙂", sort_order="2")
    response = client.post("/verwaltung/chat-elemente/", data, secure=True)
    assert response.status_code == 400
    assert response.context["asset_form"].non_field_errors()
    data["label"] = "Korrigiert"
    assert client.post("/verwaltung/chat-elemente/", data, secure=True).status_code == 302
    assert ChatAsset.objects.get(label="Korrigiert").value == "🙂"


@pytest.mark.django_db
def test_portal_admin_can_edit_chat_room_and_detail_keeps_room_list(client, admin_user, school_class):
    client.force_login(admin_user)
    room = ChatRoom.objects.create(
        school_class=school_class,
        school_year=school_class.school_year,
        title="Elternrunde",
    )

    response = client.post(
        "/chat/",
        {
            "action": "save",
            "room_id": str(room.public_id),
            "title": "Elternrunde 2026",
            "audience": "guardians",
            "appearance": "modern",
            "is_open": "on",
        },
        secure=True,
    )
    assert response.status_code == 302
    room.refresh_from_db()
    assert room.title == "Elternrunde 2026"
    assert room.audience == "guardians"
    assert room.appearance == "modern"

    archived = client.post(
        "/chat/",
        {"action": "archive", "room_id": str(room.public_id)},
        secure=True,
    )
    assert archived.status_code == 302
    room.refresh_from_db()
    assert not room.is_open

    detail = client.get(f"/chat/{room.public_id}/ansicht/", secure=True)
    assert detail.status_code == 200
    content = detail.content.decode()
    assert "Elternrunde 2026" in content
    assert "Keine Chaträume verfügbar." not in content


@pytest.mark.django_db
def test_admin_can_manage_explicit_chat_members_and_moderator_role(client, admin_user, school_class):
    room = ChatRoom.objects.create(
        school_class=school_class,
        school_year=school_class.school_year,
        title="Arbeitsgruppe",
    )
    member_user = UserAccount.objects.create_user(
        email="chat-member@example.test", password="Safe-Test-Password-123!"
    )
    person = Person.objects.create(user=member_user, first_name="Mina", last_name="Beispiel")
    ClassMembership.objects.create(
        school_class=school_class, person=person, valid_from=school_class.school_year.starts_on
    )
    client.force_login(admin_user)

    response = client.post(
        f"/chat/{room.public_id}/ansicht/",
        {"action": "member_add", "user_id": member_user.pk, "role": "moderator"},
        secure=True,
    )
    assert response.status_code == 302
    membership = ChatRoomMember.objects.get(room=room, user=member_user)
    assert membership.role == ChatRoomMember.Role.MODERATOR
    assert "Mitglieder und Moderation" in client.get(
        f"/chat/{room.public_id}/ansicht/", secure=True
    ).content.decode()
    assert may_moderate(member_user, room)

    response = client.post(
        f"/chat/{room.public_id}/ansicht/",
        {"action": "member_role", "user_id": member_user.pk, "role": "member"},
        secure=True,
    )
    assert response.status_code == 302
    membership.refresh_from_db()
    assert membership.role == ChatRoomMember.Role.MEMBER
    assert not may_moderate(member_user, room)

    outsider = UserAccount.objects.create_user(
        email="chat-outsider@example.test", password="Safe-Test-Password-123!"
    )
    outsider_person = Person.objects.create(user=outsider, first_name="Noah", last_name="Außerhalb")
    ClassMembership.objects.create(
        school_class=school_class, person=outsider_person, valid_from=school_class.school_year.starts_on
    )
    with pytest.raises(PermissionDenied):
        require_room_access(outsider, room)

    response = client.post(
        f"/chat/{room.public_id}/ansicht/",
        {"action": "member_remove", "user_id": member_user.pk},
        secure=True,
    )
    assert response.status_code == 302
    assert ChatRoomMember.objects.get(room=room, user=member_user).active
    response = client.post(
        f"/chat/{room.public_id}/ansicht/",
        {"action": "member_reset"},
        secure=True,
    )
    assert response.status_code == 302
    assert not ChatRoomMember.objects.get(room=room, user=member_user).active
    require_room_access(outsider, room)


@pytest.mark.django_db
def test_member_add_rejects_user_outside_room_audience(client, admin_user, school_class):
    room = ChatRoom.objects.create(
        school_class=school_class,
        school_year=school_class.school_year,
        title="Schülerraum",
        audience=ChatRoom.Audience.STUDENTS,
    )
    user = UserAccount.objects.create_user(
        email="chat-not-student@example.test", password="Safe-Test-Password-123!"
    )
    person = Person.objects.create(user=user, first_name="Kim", last_name="Beispiel")
    ClassMembership.objects.create(
        school_class=school_class, person=person, valid_from=school_class.school_year.starts_on
    )
    client.force_login(admin_user)
    response = client.post(
        f"/chat/{room.public_id}/ansicht/",
        {"action": "member_add", "user_id": user.pk, "role": "moderator"},
        secure=True,
    )
    assert response.status_code == 302
    assert not ChatRoomMember.objects.filter(room=room, user=user, active=True).exists()
    assert not may_moderate(user, room)


@pytest.mark.django_db
def test_graphic_sticker_upload_send_and_protected_delivery(
    client, admin_user, school_class, tmp_path, settings
):
    settings.MEDIA_ROOT = tmp_path
    image = BytesIO()
    Image.new("RGBA", (90, 70), (255, 0, 0, 127)).save(image, format="PNG")
    client.force_login(admin_user)
    response = client.post(
        "/verwaltung/chat-elemente/",
        {
            "action": "save", "kind": "sticker", "label": "Sternbild", "value": "",
            "sort_order": "1", "is_active": "on",
            "image": SimpleUploadedFile("bild.png", image.getvalue(), content_type="image/png"),
        },
        secure=True,
    )
    assert response.status_code == 302
    asset = ChatAsset.objects.get(label="Sternbild")
    assert asset.image.name.endswith(".png")
    with asset.image.open("rb") as stored:
        with Image.open(stored) as processed:
            assert processed.size == (90, 70)
            assert processed.format == "PNG"
            assert not processed.info

    room = ChatRoom.objects.create(
        school_class=school_class, school_year=school_class.school_year, title="Grafik-Test"
    )
    sent = client.post(
        f"/chat/{room.public_id}/ansicht/",
        {"body": "", "sticker_id": str(asset.pk)}, secure=True,
    )
    assert sent.status_code == 302
    message = ChatMessage.objects.get(room=room)
    assert message.sticker_id == asset.pk
    detail = client.get(f"/chat/{room.public_id}/ansicht/", secure=True)
    assert b"chat-message-sticker" in detail.content
    assert client.get(f"/chat/sticker-assets/{asset.pk}/image/", secure=True).status_code == 200
    client.logout()
    assert client.get(f"/chat/sticker-assets/{asset.pk}/image/", secure=True).status_code != 200

    client.force_login(admin_user)
    asset.is_active = False
    asset.save(update_fields=["is_active"])
    assert client.get(f"/chat/sticker-assets/{asset.pk}/image/", secure=True).status_code == 200
    assert client.post(
        f"/chat/{room.public_id}/ansicht/",
        {"body": "", "sticker_id": str(asset.pk)}, secure=True,
    ).status_code == 400
    assert ChatMessage.objects.filter(room=room).count() == 1
    replacement = BytesIO()
    Image.new("RGB", (20, 20), "blue").save(replacement, format="PNG")
    original_name = asset.image.name
    assert client.post(
        "/verwaltung/chat-elemente/",
        {
            "action": "save", "asset_id": asset.pk, "kind": "sticker",
            "label": "Sternbild", "value": "", "sort_order": "1",
            "image": SimpleUploadedFile("ersatz.png", replacement.getvalue(), content_type="image/png"),
        }, secure=True,
    ).status_code == 400
    asset.refresh_from_db()
    assert asset.image.name == original_name
    client.post(
        "/verwaltung/chat-elemente/", {"action": "delete", "asset_id": asset.pk}, secure=True
    )
    assert ChatAsset.objects.filter(pk=asset.pk).exists()


@pytest.mark.django_db
def test_invalid_sticker_image_does_not_create_asset(client, admin_user, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    client.force_login(admin_user)
    response = client.post(
        "/verwaltung/chat-elemente/",
        {
            "action": "save", "kind": "sticker", "label": "Ungültig", "value": "",
            "sort_order": "1", "is_active": "on",
            "image": SimpleUploadedFile("bild.gif", b"GIF89a", content_type="image/gif"),
        }, secure=True,
    )
    assert response.status_code == 400
    assert not ChatAsset.objects.filter(label="Ungültig").exists()


@pytest.mark.django_db
def test_missing_catalog_file_returns_not_found(client, admin_user, school_class, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    client.force_login(admin_user)
    asset = ChatAsset.objects.create(
        kind=ChatAsset.Kind.STICKER, label="Fehlende Datei", value="",
        image="chat/stickers/opaque/does-not-exist.png",
    )
    assert client.get(f"/chat/sticker-assets/{asset.pk}/image/", secure=True).status_code == 404
