from types import SimpleNamespace

import pytest
from pywebpush import WebPushException

from web_push_kit import (
    DeliveryStatus,
    NotificationPayload,
    Subscription,
    VapidConfig,
    WebPushSender,
)


@pytest.fixture
def subscription() -> Subscription:
    return Subscription("https://push.example.test/secret-endpoint", "Public_key-1", "Auth_key-1")


@pytest.fixture
def payload() -> NotificationPayload:
    return NotificationPayload("Titel", "Inhalt", "/target", "general", "message-1")


@pytest.fixture
def config() -> VapidConfig:
    return VapidConfig("public-vapid", "private-vapid", "mailto:admin@example.test")


def webpush_error(status: int | None, sensitive_text: str = "sensitive") -> WebPushException:
    error = WebPushException(sensitive_text)
    error.response = None if status is None else SimpleNamespace(status_code=status)
    return error


def test_successful_delivery(config, subscription, payload) -> None:
    calls = []
    result = WebPushSender(config, transport=lambda **kwargs: calls.append(kwargs)).send(
        subscription, payload
    )
    assert result.status is DeliveryStatus.DELIVERED
    assert len(calls) == 1


@pytest.mark.parametrize("status", [404, 410])
def test_gone_subscription_is_stale(status, config, subscription, payload) -> None:
    def transport(**_kwargs):
        raise webpush_error(status)

    result = WebPushSender(config, transport=transport).send(subscription, payload)
    assert result.status is DeliveryStatus.STALE
    assert result.should_remove_subscription is True


@pytest.mark.parametrize(
    "error", [TimeoutError("secret"), ConnectionError("secret"), webpush_error(503)]
)
def test_temporary_transport_failure(error, config, subscription, payload) -> None:
    def transport(**_kwargs):
        raise error

    result = WebPushSender(config, transport=transport).send(subscription, payload)
    assert result.status is DeliveryStatus.TEMPORARY_FAILURE


@pytest.mark.parametrize("error", [webpush_error(400), ValueError("secret payload")])
def test_permanent_failure_is_opaque(error, config, subscription, payload) -> None:
    def transport(**_kwargs):
        raise error

    result = WebPushSender(config, transport=transport).send(subscription, payload)
    rendered = repr(result)
    assert result.status is DeliveryStatus.PERMANENT_FAILURE
    assert "secret" not in rendered
    assert subscription.endpoint not in rendered
    assert subscription.auth not in rendered
    assert config.private_key not in rendered


def test_application_decides_when_to_delete(config, subscription, payload) -> None:
    deleted = []

    def transport(**_kwargs):
        raise webpush_error(410)

    result = WebPushSender(config, transport=transport).send(subscription, payload)
    if result.should_remove_subscription:
        deleted.append(subscription.endpoint)
    assert deleted == [subscription.endpoint]
