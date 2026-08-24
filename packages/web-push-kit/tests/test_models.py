import json

import pytest

from web_push_kit import NotificationAction, NotificationPayload, Subscription, VapidConfig


def subscription(**changes: str) -> Subscription:
    values = {
        "endpoint": "https://push.example.test/subscription/abc",
        "p256dh": "Abc_123-xyz",
        "auth": "Auth_123-xyz",
    }
    values.update(changes)
    return Subscription(**values)


def payload(**changes: object) -> NotificationPayload:
    values = {
        "title": "Neue Mitteilung",
        "body": "Details sind nach der Anmeldung verfügbar.",
        "url": "/messages/42",
        "category": "general",
        "message_id": "msg-42",
    }
    values.update(changes)
    return NotificationPayload(**values)


def test_valid_subscription_has_webpush_shape_and_redacted_keys() -> None:
    item = subscription()
    assert item.as_webpush_info()["keys"]["auth"] == "Auth_123-xyz"
    assert item.endpoint not in repr(item)
    assert "Auth_123-xyz" not in repr(item)
    assert "Abc_123-xyz" not in repr(item)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("endpoint", "http://push.example.test/value"),
        ("endpoint", "https://user:pass@push.example.test/value"),
        ("p256dh", "not base64!"),
        ("auth", ""),
    ],
)
def test_invalid_subscription_is_rejected(field: str, value: str) -> None:
    with pytest.raises((TypeError, ValueError)):
        subscription(**{field: value})


def test_valid_payload_serializes_to_compact_json() -> None:
    item = payload(actions=(NotificationAction("open", "Öffnen", "/messages/42"),))
    result = json.loads(item.to_json())
    assert result["message_id"] == "msg-42"
    assert result["actions"] == [
        {"action": "open", "title": "Öffnen", "url": "/messages/42"}
    ]
    assert ": " not in item.to_json()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", "x" * 121),
        ("body", "x" * 501),
        ("category", "x" * 65),
        ("message_id", "x" * 129),
    ],
)
def test_payload_field_lengths_are_bounded(field: str, value: str) -> None:
    with pytest.raises(ValueError, match="exceeds"):
        payload(**{field: value})


def test_payload_rejects_too_many_actions() -> None:
    actions = tuple(NotificationAction(f"action-{number}", "Ausführen") for number in range(3))
    with pytest.raises(ValueError, match="at most 2"):
        payload(actions=actions)


@pytest.mark.parametrize(
    "url",
    ["https://", "http://example.test/x", "//example.test/x", "javascript:alert(1)"],
)
def test_payload_rejects_unsafe_url(url: str) -> None:
    with pytest.raises(ValueError):
        payload(url=url)


def test_vapid_private_key_is_not_in_repr() -> None:
    config = VapidConfig("public-material", "private-material", "mailto:admin@example.test")
    assert "private-material" not in repr(config)
