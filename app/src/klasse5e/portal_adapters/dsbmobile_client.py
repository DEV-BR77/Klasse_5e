"""Small, dependency-free DSBmobile client.

The public reference implementation uses the DSBmobile Android request
envelope: JSON -> gzip -> base64, posted to ``JsonHandler.ashx/GetData``.
This module keeps that protocol isolated from Django views so the adapter can
be tested with recorded responses before any school credentials are used.
"""

import base64
import gzip
import json
import uuid
from datetime import datetime, timezone
from urllib import request


class DSBMobileError(RuntimeError):
    """A safe, user-facing DSBmobile failure without credential details."""


class DSBMobileClient:
    endpoint = "https://www.dsbmobile.de/JsonHandler.ashx/GetData"

    def __init__(self, username, password, *, opener=None, timeout=20):
        self.username = username
        self.password = password
        self.opener = opener or request.urlopen
        self.timeout = timeout

    def fetch(self):
        now = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        args = {
            "UserId": self.username,
            "UserPw": self.password,
            "Language": "de",
            "Device": "Nexus 4",
            "AppId": str(uuid.uuid4()),
            "AppVersion": "2.5.9",
            "OsVersion": "27 8.1.0",
            "PushId": "",
            "BundleId": "de.heinekingmedia.dsbmobile",
            "Date": now,
            "LastUpdate": now,
        }
        compressed = gzip.compress(json.dumps(args, separators=(",", ":")).encode())
        payload = {"req": {"Data": base64.b64encode(compressed).decode(), "DataType": 1}}
        body = json.dumps(payload, separators=(",", ":")).encode()
        req = request.Request(
            self.endpoint,
            data=body,
            method="POST",
            headers={
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 8.1.0; Nexus 4)",
                "Accept-Encoding": "gzip, deflate",
                "Content-Type": "application/json;charset=utf-8",
            },
        )
        try:
            with self.opener(req, timeout=self.timeout) as response:
                envelope = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # deliberately do not expose transport details
            raise DSBMobileError("DSBmobile ist derzeit nicht erreichbar.") from exc
        try:
            raw = base64.b64decode(envelope["d"])
            result = json.loads(gzip.decompress(raw).decode("utf-8"))
        except (KeyError, TypeError, ValueError, OSError) as exc:
            raise DSBMobileError("DSBmobile hat eine ungültige Antwort geliefert.") from exc
        if result.get("Resultcode") not in (0, "0", None):
            raise DSBMobileError("DSBmobile hat den Zugang abgelehnt.")
        return result

    @staticmethod
    def items(result, title):
        """Return child records below an ``Inhalte`` menu item by title."""
        for item in result.get("ResultMenuItems", []):
            if str(item.get("Title", "")).casefold() != "inhalte":
                continue
            for section in item.get("Childs", []):
                if str(section.get("Title", "")).casefold() != title.casefold():
                    continue
                root = section.get("Root") or {}
                return [item for item in root.get("Childs", []) if isinstance(item, dict)]
        return []

    @classmethod
    def normalize(cls, result):
        return {
            "timetables": [
                {
                    "id": item.get("Id"),
                    "group": item.get("Title", ""),
                    "date": item.get("Date", ""),
                    "detail": child.get("Detail", ""),
                    "title": child.get("Title", ""),
                }
                for item in cls.items(result, "Pläne")
                for child in item.get("Childs", [])
                if isinstance(child, dict)
            ],
            "notices": [
                {
                    "id": item.get("Id"),
                    "date": item.get("Date", ""),
                    "title": item.get("Title", ""),
                    "detail": item.get("Detail", ""),
                }
                for item in cls.items(result, "News")
            ],
        }
