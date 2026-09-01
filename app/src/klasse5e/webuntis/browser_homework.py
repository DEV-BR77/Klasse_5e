import json
from urllib.parse import urlparse

from .client import ALLOWED_HOST, InvalidCredentials, InvalidResponse, TemporaryNetworkError

LOGIN_PATH = "/WebUntis/"
HOMEWORK_PAGE_PATH = "/student-homework"
HOMEWORK_API_PATH = "/WebUntis/api/homeworks/lessons"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


class BrowserTimeout(TemporaryNetworkError):
    code = "browser_timeout"


class BrowserCrashed(TemporaryNetworkError):
    code = "browser_crashed"


def _allowed_url(url, path):
    parsed = urlparse(url)
    return (
        parsed.scheme == "https"
        and parsed.hostname == ALLOWED_HOST
        and parsed.port is None
        and parsed.path == path
    )


class PlaywrightHomeworkClient:
    def __init__(self, username, password, *, server=ALLOWED_HOST, school="thgwob", timeout_ms=30_000):
        if server != ALLOWED_HOST:
            raise ValueError("WebUntis-Server nicht freigegeben")
        self.username = username
        self.password = password
        self.server = server
        self.school = school
        self.timeout_ms = min(max(int(timeout_ms), 5_000), 45_000)

    def fetch(self):
        try:
            from playwright.sync_api import TimeoutError as PlaywrightTimeout
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise BrowserCrashed() from exc
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    headless=True,
                    args=["--disable-dev-shm-usage", "--no-first-run", "--disable-extensions"],
                )
                try:
                    context = browser.new_context(
                        locale="de-DE",
                        service_workers="block",
                        viewport={"width": 1024, "height": 768},
                    )
                    try:
                        page = context.new_page()
                        page.set_default_timeout(self.timeout_ms)
                        page.route(
                            "**/*",
                            lambda route: route.abort()
                            if route.request.resource_type in {"image", "media", "font"}
                            else route.continue_(),
                        )
                        login_url = f"https://{self.server}{LOGIN_PATH}?school={self.school}#/basic/login"
                        if not _allowed_url(login_url, LOGIN_PATH):
                            raise ValueError("Nicht freigegebener Loginpfad")
                        page.goto(login_url, wait_until="domcontentloaded")
                        page.locator('input[type="text"]').first.fill(self.username)
                        password = page.locator('input[type="password"]').first
                        password.fill(self.password)
                        page.locator('button[type="submit"]').first.click()
                        page.wait_for_timeout(1_000)
                        if password.is_visible():
                            raise InvalidCredentials()
                        homework_url = f"https://{self.server}{HOMEWORK_PAGE_PATH}"
                        if not _allowed_url(homework_url, HOMEWORK_PAGE_PATH):
                            raise ValueError("Nicht freigegebener Hausaufgabenpfad")
                        with page.expect_response(
                            lambda response: _allowed_url(response.url, HOMEWORK_API_PATH)
                            and response.request.method == "GET"
                            and response.status == 200,
                            timeout=self.timeout_ms,
                        ) as response_info:
                            page.goto(homework_url, wait_until="domcontentloaded")
                        response = response_info.value
                        payload = response.json()
                        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                        if len(encoded) > MAX_RESPONSE_BYTES or not isinstance(payload, dict | list):
                            raise InvalidResponse()
                        return payload
                    finally:
                        context.close()
                finally:
                    browser.close()
        except PlaywrightTimeout as exc:
            raise BrowserTimeout() from exc
        except (InvalidResponse, InvalidCredentials, ValueError):
            raise
        except Exception as exc:
            raise BrowserCrashed() from exc
