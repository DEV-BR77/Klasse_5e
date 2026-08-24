"""Delivery adapter around pywebpush with privacy-safe outcomes."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from pywebpush import WebPushException, webpush

from .models import NotificationPayload, Subscription, VapidConfig


class DeliveryStatus(StrEnum):
    DELIVERED = "delivered"
    STALE = "stale"
    TEMPORARY_FAILURE = "temporary_failure"
    PERMANENT_FAILURE = "permanent_failure"


@dataclass(frozen=True, slots=True)
class DeliveryResult:
    """A non-sensitive result; it never includes endpoint, keys or payload."""

    status: DeliveryStatus
    http_status: int | None = None
    reason: str | None = None

    @property
    def should_remove_subscription(self) -> bool:
        return self.status is DeliveryStatus.STALE


WebPushCallable = Callable[..., Any]


class WebPushSender:
    """Synchronous sender with injectable transport for deterministic tests."""

    def __init__(self, config: VapidConfig, *, transport: WebPushCallable = webpush) -> None:
        self._config = config
        self._transport = transport

    def send(
        self, subscription: Subscription, payload: NotificationPayload, *, timeout: int = 10
    ) -> DeliveryResult:
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        try:
            self._transport(
                subscription_info=subscription.as_webpush_info(),
                data=payload.to_json(),
                vapid_private_key=self._config.private_key,
                vapid_claims={"sub": self._config.subject},
                timeout=timeout,
            )
            return DeliveryResult(DeliveryStatus.DELIVERED)
        except WebPushException as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            return _result_for_http_status(status)
        except (TimeoutError, ConnectionError):
            return DeliveryResult(DeliveryStatus.TEMPORARY_FAILURE, reason="transport_unavailable")
        except Exception:
            # Unexpected transport errors are intentionally opaque. Treating them
            # as permanent avoids an unbounded retry loop decided inside this kit.
            return DeliveryResult(DeliveryStatus.PERMANENT_FAILURE, reason="transport_error")


def _result_for_http_status(status: int | None) -> DeliveryResult:
    if status in (404, 410):
        return DeliveryResult(DeliveryStatus.STALE, http_status=status, reason="subscription_gone")
    if status is None or status in (408, 425, 429) or status >= 500:
        return DeliveryResult(
            DeliveryStatus.TEMPORARY_FAILURE,
            http_status=status,
            reason="push_service_unavailable",
        )
    return DeliveryResult(
        DeliveryStatus.PERMANENT_FAILURE,
        http_status=status,
        reason="push_service_rejected",
    )
