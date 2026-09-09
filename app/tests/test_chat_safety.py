from io import BytesIO
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from test_phase7 import member

from klasse5e.chat.models import ChatMessage, ChatRoom
from klasse5e.chat.safety import filter_chat_language, pixelate_image
from klasse5e.chat.services import _image_safety_status, create_message


@pytest.fixture
def room(school_class):
    return ChatRoom.objects.create(
        school_class=school_class,
        school_year=school_class.school_year,
        title="Sicherer Klassenchat",
    )


def test_german_insults_are_fully_masked_including_simple_bypasses():
    filtered, hits = filter_chat_language(
        "Du IDIOT, du A-r-s-c-h-l-o-c-h. Bitte verpiss dich."
    )

    assert hits == 3
    assert "IDIOT" not in filtered
    assert "A-r-s-c-h-l-o-c-h" not in filtered
    assert "verpiss dich" not in filtered
    assert "•••••" in filtered


def test_filter_does_not_mask_innocent_word_parts():
    text = "Das war eine idiotische Idee für die Kuhweide."
    assert filter_chat_language(text) == (text, 0)


def _checkerboard(size=240):
    image = Image.new("RGB", (size, size))
    pixels = image.load()
    for y in range(size):
        for x in range(size):
            pixels[x, y] = (255, 255, 255) if (x + y) % 2 else (0, 0, 0)
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def test_pixelated_derivative_keeps_dimensions_and_removes_fine_detail():
    original = _checkerboard()
    derivative = pixelate_image(original)

    with Image.open(BytesIO(derivative)) as image:
        assert image.size == (240, 240)
        assert image.format == "JPEG"
        colors = image.resize((24, 24)).getcolors(maxcolors=1_000)
        assert colors is not None
        assert len(colors) < 20


@pytest.mark.django_db
def test_unapproved_image_is_delivered_only_as_pixelated_derivative(client, room):
    user = member(room)
    original = _checkerboard()
    message = ChatMessage.objects.create(
        room=room,
        author=user,
        attachment=SimpleUploadedFile("bild.png", original, content_type="image/png"),
        attachment_name="bild.png",
        attachment_content_type="image/png",
        attachment_safety_status="blocked",
    )
    client.force_login(user)

    response = client.get(f"/chat/nachricht/{message.public_id}/anhang/")
    result = b"".join(response.streaming_content)

    assert response.status_code == 200
    assert response["Content-Type"] == "image/jpeg"
    assert response["Cache-Control"] == "private, no-store"
    assert result != original

    membership = user.person.classmembership_set.get()
    membership.status = "ended"
    membership.save(update_fields=["status"])
    assert client.get(f"/chat/nachricht/{message.public_id}/anhang/").status_code == 404


@pytest.mark.django_db
def test_uploaded_image_is_reencoded_before_classification_and_storage(room):
    user = member(room)
    upload = SimpleUploadedFile("ferienbild.png", _checkerboard(), content_type="image/png")
    with patch(
        "klasse5e.biometrics.client.VisionClient.classify_image_safety",
        return_value={"decision": "approved"},
    ):
        message = create_message(room, user, "", attachment=upload)

    assert message.attachment_name == "ferienbild.png"
    assert message.attachment_content_type == "image/jpeg"
    with message.attachment.open("rb") as stored, Image.open(stored) as image:
        assert image.format == "JPEG"
        assert image.getexif() == {}


def test_image_classifier_failure_defaults_to_pixelation():
    attachment = SimpleUploadedFile("bild.png", _checkerboard(), content_type="image/png")
    with patch(
        "klasse5e.biometrics.client.VisionClient.classify_image_safety",
        side_effect=OSError("synthetic failure"),
    ):
        assert _image_safety_status(attachment) == "pending"


@pytest.mark.django_db
def test_edited_message_is_filtered_too(client, room):
    author = member(room)
    message = ChatMessage.objects.create(room=room, author=author, body="Zunächst harmlos")
    client.force_login(author)

    response = client.patch(
        f"/chat/messages/{message.public_id}/",
        data='{"body":"Du bist ein Idiot"}',
        content_type="application/json",
    )

    assert response.status_code == 204
    message.refresh_from_db()
    assert message.body == "Du bist ein •••••"
    assert message.language_filter_hits == 1
