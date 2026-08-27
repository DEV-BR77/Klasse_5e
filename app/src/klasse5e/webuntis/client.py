"""Framework-neutral, read-only WebUntis JSON-RPC/REST client.

The endpoint set is deliberately finite. No arbitrary RPC or raw response API
is exposed to Django or users.
"""

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

ALLOWED_HOST = "thgwob.webuntis.com"
ALLOWED_RPC = {
    "getTimetable",
    "getSubstitutions",
    "getHolidays",
    "getTimegridUnits",
    "getCurrentSchoolyear",
}
ALLOWED_REST = {
    "students": "/api/rest/view/v1/app/data",
    "timetable_weekly": "/api/public/timetable/weekly/data",
    "homework": "/api/homeworks/lessons",
    "exams": "/api/exams",
    "absences": "/api/classreg/absences/students",
    "messages": "/api/rest/view/v1/messages",
}


class WebUntisClientError(Exception):
    code = "unknown_external_error"


class InvalidCredentials(WebUntisClientError):
    code = "invalid_credentials"


class MfaRequired(WebUntisClientError):
    code = "mfa_or_sso_required"


class NotAuthorized(WebUntisClientError):
    code = "not_authorized"


class EndpointUnsupported(WebUntisClientError):
    code = "unsupported"


class TemporaryNetworkError(WebUntisClientError):
    code = "temporary_network_error"


class RateLimited(WebUntisClientError):
    code = "rate_limit"


class InvalidResponse(WebUntisClientError):
    code = "invalid_response"


@dataclass(frozen=True)
class EndpointResult:
    key: str
    status: str
    count: int | None = None


class WebUntisClient:
    def __init__(
        self,
        username,
        password,
        *,
        server=ALLOWED_HOST,
        school="thgwob",
        timeout=10.0,
        user_agent="Klasse-5e-WebUntis-Pilot/9A",
    ):
        if server != ALLOWED_HOST:
            raise ValueError("WebUntis-Server nicht freigegeben")
        self.base = f"https://{server}/WebUntis"
        self.school = school
        self.username = username
        self.password = password
        self.timeout = timeout
        self.user_agent = user_agent
        self._session_id = None
        self._jwt = None
        self._last_request = 0.0

    def _request(self, url, payload=None, headers=None, attempts=2):
        wait = 0.25
        for attempt in range(attempts):
            delay = 0.15 - (time.monotonic() - self._last_request)
            if delay > 0:
                time.sleep(delay)
            request_headers = {"User-Agent": self.user_agent, "Accept": "application/json"}
            if payload is not None:
                request_headers["Content-Type"] = "application/json"
            request_headers.update(headers or {})
            request = urllib.request.Request(
                url,
                data=json.dumps(payload).encode() if payload is not None else None,
                headers=request_headers,
                method="POST" if payload is not None else "GET",
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    self._last_request = time.monotonic()
                    if response.status == 429:
                        raise RateLimited()
                    return json.loads(response.read().decode())
            except urllib.error.HTTPError as exc:
                if exc.code in (401, 403):
                    raise NotAuthorized() from exc
                if exc.code == 429:
                    raise RateLimited() from exc
                if 500 <= exc.code < 600 and attempt + 1 < attempts:
                    time.sleep(wait)
                    wait *= 2
                    continue
                raise TemporaryNetworkError() from exc
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                if attempt + 1 < attempts:
                    time.sleep(wait)
                    wait *= 2
                    continue
                raise TemporaryNetworkError() from exc
        raise TemporaryNetworkError()

    def login(self):
        result = self._request(
            f"{self.base}/jsonrpc.do?school={self.school}",
            {
                "id": 1,
                "method": "authenticate",
                "params": {
                    "user": self.username,
                    "password": self.password,
                    "client": self.user_agent,
                },
                "jsonrpc": "2.0",
            },
            attempts=1,
        )
        if result.get("error"):
            message = str(result["error"]).lower()
            if "mfa" in message or "sso" in message or "two" in message:
                raise MfaRequired()
            raise InvalidCredentials()
        self._session_id = result.get("result", {}).get("sessionId")
        if not self._session_id:
            raise InvalidResponse()
        return self

    def rpc(self, method, params=None):
        if method not in ALLOWED_RPC:
            raise EndpointUnsupported(method)
        if not self._session_id:
            self.login()
        result = self._request(
            f"{self.base}/jsonrpc.do?school={self.school}",
            {"id": 1, "method": method, "params": params or {}, "jsonrpc": "2.0"},
            {"Cookie": f"JSESSIONID={self._session_id}"},
        )
        if result.get("error"):
            raise NotAuthorized()
        return result.get("result")

    def rest(self, key, *, params=None):
        path = ALLOWED_REST.get(key)
        if not path:
            raise EndpointUnsupported(key)
        if not self._session_id:
            self.login()
        result = self._request(
            f"{self.base}{path}",
            headers={
                "Cookie": f"JSESSIONID={self._session_id}",
                **({"Authorization": f"Bearer {self._jwt}"} if self._jwt else {}),
            },
        )
        if not isinstance(result, dict | list):
            raise InvalidResponse()
        return result

    def close(self):
        if self._session_id:
            try:
                self._request(
                    f"{self.base}/jsonrpc.do?school={self.school}",
                    {"id": 1, "method": "logout", "params": {}, "jsonrpc": "2.0"},
                    {"Cookie": f"JSESSIONID={self._session_id}"},
                    attempts=1,
                )
            except WebUntisClientError:
                pass
        self._session_id = None
        self._jwt = None

    def __enter__(self):
        return self.login()

    def __exit__(self, *_):
        self.close()
