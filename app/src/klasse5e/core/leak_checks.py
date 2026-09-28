"""Privacy-preserving breach checks used after successful authentication."""

import hashlib
import json
import logging
from datetime import timedelta
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def _get_json(url):
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "KlassID-security-check"})
    with urlopen(request, timeout=settings.LEAK_CHECK_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def check_email(email):
    """Return (state, count) without storing the address or breach details."""
    try:
        payload = _get_json(f"{settings.XPOSEDORNOT_CHECK_URL}/{quote(email, safe='')}")
        if isinstance(payload, dict) and payload.get("Error"):
            return "clear", 0
        if isinstance(payload, dict):
            for key in ("breaches", "Breaches", "breach", "data"):
                value = payload.get(key)
                if isinstance(value, list):
                    return ("found", len(value)) if value else ("clear", 0)
        return "found", 1
    except Exception:
        logger.warning("Email leak check unavailable", exc_info=True)
        return "unknown", 0


def check_password(password):
    """Check only a five-character SHA-1 prefix; never send the password/full hash."""
    digest = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = digest[:5], digest[5:]
    try:
        request = Request(
            f"{settings.HIBP_PASSWORD_RANGE_URL}/{prefix}",
            headers={"User-Agent": "KlassID-security-check", "Add-Padding": "true"},
        )
        with urlopen(request, timeout=settings.LEAK_CHECK_TIMEOUT_SECONDS) as response:
            matches = response.read().decode("utf-8").splitlines()
        for line in matches:
            candidate, _, count = line.partition(":")
            if candidate.upper() == suffix:
                return "found", int(count or 1)
        return "clear", 0
    except Exception:
        logger.warning("Password leak check unavailable", exc_info=True)
        return "unknown", 0


def inspect_successful_login(user, submitted_password):
    now = timezone.now()
    changed = False
    if not user.email_leak_checked_at or now - user.email_leak_checked_at >= timedelta(hours=24):
        state, count = check_email(user.email)
        if state != "unknown":
            user.email_leak_state, user.email_leak_count = state, count
        if state != "unknown":
            user.email_leak_checked_at = now
            changed = True
    if submitted_password and (not user.password_leak_checked_at or now - user.password_leak_checked_at >= timedelta(hours=24)):
        state, count = check_password(submitted_password)
        if state != "unknown":
            user.password_leak_state, user.password_leak_count = state, count
        if state != "unknown":
            user.password_leak_checked_at = now
            changed = True
    if changed:
        user.save(update_fields=["email_leak_state", "email_leak_count", "email_leak_checked_at", "password_leak_state", "password_leak_count", "password_leak_checked_at"])
    return user.email_leak_state == "found", user.password_leak_state == "found"
