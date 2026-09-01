import hashlib
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from django.db import transaction
from django.utils import timezone

from .models import ItslearningCalendarItem, ItslearningUpdate

MAX_FEED_BYTES = 2 * 1024 * 1024
ALLOWED_HOST = "wob.itslearning.com"
def _safe_external_url(value):
    value = (value or "").strip()
    if not value:
        return ""
    parsed = urlparse(value)
    return value[:800] if parsed.scheme == "https" and parsed.hostname == ALLOWED_HOST else ""


def _error_code(exc):
    if isinstance(exc, ValueError):
        return "invalid_feed"
    if isinstance(exc, TimeoutError | OSError):
        return "temporary_network_error"
    return "sync_failed"




def _fetch(url):
    parsed = urlparse(url)
    if parsed.scheme not in {"https", "webcal"} or parsed.hostname != ALLOWED_HOST:
        raise ValueError("Nicht erlaubte Feed-Adresse")
    target = parsed._replace(scheme="https").geturl()
    request = urllib.request.Request(target, headers={"User-Agent": "Klasse5e/0.3 feed reader"})
    with urllib.request.urlopen(request, timeout=12) as response:
        content_type = response.headers.get_content_type()
        if content_type not in {
            "application/rss+xml",
            "application/xml",
            "text/xml",
            "text/calendar",
            "text/plain",
            # Wolfsburg liefert CalendarFeed derzeit trotz gültigem iCal als text/html.
            "text/html",
        }:
            raise ValueError("Unerwarteter Feed-Inhalt")
        data = response.read(MAX_FEED_BYTES + 1)
    if len(data) > MAX_FEED_BYTES:
        raise ValueError("Feed ist zu groß")
    return data


def sync_course(course):
    if not course.rss_url:
        return 0
    root = ET.fromstring(_fetch(course.rss_url))
    if root.tag.casefold() != "rss":
        raise ValueError("RSS-Feed ist nicht im erwarteten Format")
    created = 0
    for item in root.findall(".//item")[:100]:
        title = (item.findtext("title") or "Aktualisierung").strip()[:300]
        link = _safe_external_url(item.findtext("link"))
        summary = (item.findtext("description") or "").strip()[:8000]
        raw_date = (item.findtext("pubDate") or "").strip()
        published = parsedate_to_datetime(raw_date) if raw_date else None
        if published and timezone.is_naive(published):
            published = timezone.make_aware(published)
        fingerprint = hashlib.sha256(f"{title}\n{link}\n{raw_date}".encode()).hexdigest()
        _, was_created = ItslearningUpdate.objects.get_or_create(
            course=course,
            fingerprint=fingerprint,
            defaults={"title": title, "summary": summary, "url": link, "published_at": published},
        )
        created += int(was_created)
    return created


def _unfold_ical(text):
    return re.sub(r"\r?\n[ \t]", "", text).splitlines()


def _ical_datetime(value):
    value = value.strip()
    if len(value) == 8:
        result = datetime.strptime(value, "%Y%m%d")
    elif value.endswith("Z"):
        result = datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=ZoneInfo("UTC"))
    else:
        result = datetime.strptime(value[:15], "%Y%m%dT%H%M%S")
    return (
        timezone.make_aware(result, ZoneInfo("Europe/Berlin"))
        if timezone.is_naive(result)
        else result
    )


def sync_calendar(connection):
    if not connection.calendar_url:
        return 0
    events, current = [], None
    calendar_text = _fetch(connection.calendar_url).decode("utf-8-sig", errors="replace")
    if not calendar_text.lstrip().startswith("BEGIN:VCALENDAR"):
        raise ValueError("Kalender-Feed ist nicht im erwarteten Format")
    for line in _unfold_ical(calendar_text):
        if line == "BEGIN:VEVENT":
            current = {}
        elif line == "END:VEVENT" and current is not None:
            events.append(current)
            current = None
        elif current is not None and ":" in line:
            key, value = line.split(":", 1)
            current[key.split(";", 1)[0]] = value.replace("\\n", "\n").replace("\\,", ",")
    seen, changed = set(), 0
    with transaction.atomic():
        for event in events[:500]:
            uid = event.get("UID") or hashlib.sha256(repr(event).encode()).hexdigest()
            if not event.get("DTSTART"):
                continue
            seen.add(uid)
            _, was_created = ItslearningCalendarItem.objects.update_or_create(
                connection=connection,
                uid=uid[:300],
                defaults={
                    "title": event.get("SUMMARY", "Termin")[:300],
                    "starts_at": _ical_datetime(event["DTSTART"]),
                    "ends_at": _ical_datetime(event["DTEND"]) if event.get("DTEND") else None,
                    "description": event.get("DESCRIPTION", "")[:8000],
                    "url": _safe_external_url(event.get("URL")),
                },
            )
            changed += int(was_created)
        connection.calendar_items.exclude(uid__in=seen).delete()
    return changed


def sync_connection(connection):
    try:
        count = sync_calendar(connection)
        for course in connection.itslearningcourse_set.all():
            count += sync_course(course)
        connection.last_sync_status = "ok"
        connection.last_sync_message = f"{count} neue Einträge"
    except Exception as exc:
        connection.last_sync_status = "failed"
        connection.last_sync_message = _error_code(exc)
    connection.last_sync_at = timezone.now()
    connection.save(update_fields=["last_sync_status", "last_sync_message", "last_sync_at"])
    return connection.last_sync_status == "ok"
