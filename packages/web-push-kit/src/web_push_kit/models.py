"""Validated, framework-independent Web Push values."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit

MAX_ENDPOINT_LENGTH = 4096
MAX_KEY_LENGTH = 4096
MAX_TITLE_LENGTH = 120
MAX_BODY_LENGTH = 500
MAX_URL_LENGTH = 2048
MAX_CATEGORY_LENGTH = 64
MAX_MESSAGE_ID_LENGTH = 128
MAX_TAG_LENGTH = 128
MAX_ACTIONS = 2
MAX_ACTION_ID_LENGTH = 64
MAX_ACTION_TITLE_LENGTH = 80
MAX_PAYLOAD_BYTES = 3072

_BASE64URL = re.compile(r"^[A-Za-z0-9_-]+={0,2}$")
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")


def _required(value: str, name: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} must not be empty")
    if len(value) > maximum:
        raise ValueError(f"{name} exceeds {maximum} characters")
    return value


def _optional(value: str | None, name: str, maximum: int) -> str | None:
    if value is None:
        return None
    return _required(value, name, maximum)


def _web_url(value: str, name: str, *, relative_allowed: bool) -> str:
    _required(value, name, MAX_URL_LENGTH)
    if any(character in value for character in ("\r", "\n", "\x00")):
        raise ValueError(f"{name} contains control characters")
    if relative_allowed and value.startswith("/") and not value.startswith("//"):
        return value
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        requirement = "an internal path or HTTPS URL" if relative_allowed else "an HTTPS URL"
        raise ValueError(f"{name} must be {requirement}")
    return value


@dataclass(frozen=True, slots=True)
class Subscription:
    """Browser subscription data without application ownership or persistence."""

    endpoint: str = field(repr=False)
    p256dh: str = field(repr=False)
    auth: str = field(repr=False)

    def __post_init__(self) -> None:
        _web_url(
            _required(self.endpoint, "endpoint", MAX_ENDPOINT_LENGTH),
            "endpoint",
            relative_allowed=False,
        )
        for name, value in (("p256dh", self.p256dh), ("auth", self.auth)):
            _required(value, name, MAX_KEY_LENGTH)
            if not _BASE64URL.fullmatch(value):
                raise ValueError(f"{name} must be base64url encoded")

    def as_webpush_info(self) -> dict[str, Any]:
        return {
            "endpoint": self.endpoint,
            "keys": {"p256dh": self.p256dh, "auth": self.auth},
        }


@dataclass(frozen=True, slots=True)
class NotificationAction:
    """A neutral notification action interpreted by the service worker."""

    action: str
    title: str
    url: str | None = None

    def __post_init__(self) -> None:
        _required(self.action, "action", MAX_ACTION_ID_LENGTH)
        if not _IDENTIFIER.fullmatch(self.action):
            raise ValueError("action contains unsupported characters")
        _required(self.title, "action title", MAX_ACTION_TITLE_LENGTH)
        if self.url is not None:
            _web_url(self.url, "action url", relative_allowed=True)

    def as_dict(self) -> dict[str, str]:
        result = {"action": self.action, "title": self.title}
        if self.url is not None:
            result["url"] = self.url
        return result


@dataclass(frozen=True, slots=True)
class NotificationPayload:
    """Small, application-neutral notification data with explicit bounds."""

    title: str
    body: str
    url: str
    category: str
    message_id: str
    tag: str | None = None
    icon: str | None = None
    actions: tuple[NotificationAction, ...] = ()

    def __post_init__(self) -> None:
        _required(self.title, "title", MAX_TITLE_LENGTH)
        _required(self.body, "body", MAX_BODY_LENGTH)
        _web_url(self.url, "url", relative_allowed=True)
        _required(self.category, "category", MAX_CATEGORY_LENGTH)
        _required(self.message_id, "message_id", MAX_MESSAGE_ID_LENGTH)
        if not _IDENTIFIER.fullmatch(self.category):
            raise ValueError("category contains unsupported characters")
        if not _IDENTIFIER.fullmatch(self.message_id):
            raise ValueError("message_id contains unsupported characters")
        _optional(self.tag, "tag", MAX_TAG_LENGTH)
        if self.icon is not None:
            _web_url(self.icon, "icon", relative_allowed=True)
        if not isinstance(self.actions, tuple):
            object.__setattr__(self, "actions", tuple(self.actions))
        if len(self.actions) > MAX_ACTIONS:
            raise ValueError(f"actions must contain at most {MAX_ACTIONS} entries")
        if len({action.action for action in self.actions}) != len(self.actions):
            raise ValueError("action identifiers must be unique")
        if len(self.to_json().encode("utf-8")) > MAX_PAYLOAD_BYTES:
            raise ValueError(f"serialized payload exceeds {MAX_PAYLOAD_BYTES} bytes")

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "title": self.title,
            "body": self.body,
            "url": self.url,
            "category": self.category,
            "message_id": self.message_id,
        }
        if self.tag is not None:
            result["tag"] = self.tag
        if self.icon is not None:
            result["icon"] = self.icon
        if self.actions:
            result["actions"] = [action.as_dict() for action in self.actions]
        return result

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class VapidConfig:
    """VAPID material supplied by the embedding application's secret store."""

    public_key: str
    private_key: str = field(repr=False)
    subject: str

    def __post_init__(self) -> None:
        _required(self.public_key, "public_key", MAX_KEY_LENGTH)
        if not _BASE64URL.fullmatch(self.public_key):
            raise ValueError("public_key must be base64url encoded")
        _required(self.private_key, "private_key", MAX_KEY_LENGTH)
        _required(self.subject, "subject", MAX_URL_LENGTH)
        if self.subject.startswith("mailto:"):
            address = self.subject.removeprefix("mailto:")
            if "@" not in address or any(character in address for character in "\r\n"):
                raise ValueError("subject must contain a valid mailto address")
        else:
            _web_url(self.subject, "subject", relative_allowed=False)
