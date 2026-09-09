"""Narrow, read-only Playwright transport for Schulmanager Online."""

from dataclasses import dataclass

BASE_URL = "https://login.schulmanager-online.de"
MESSAGES_PATH = "/#/modules/messenger/messages"
LETTERS_PATH = "/#/modules/letters/view"


class BrowserError(RuntimeError):
    code = "browser_error"


class InvalidCredentials(BrowserError):
    code = "invalid_credentials"


class BrowserTimeout(BrowserError):
    code = "browser_timeout"


@dataclass(frozen=True)
class SchoolmanagerItem:
    kind: str
    external_id: str
    title: str
    changed_at: str = ""


class PlaywrightSchoolmanagerClient:
    def __init__(self, username, password, *, timeout_ms=30_000):
        self.username = username
        self.password = password
        self.timeout_ms = min(max(int(timeout_ms), 5_000), 45_000)

    def fetch(self):
        try:
            from playwright.sync_api import TimeoutError as PlaywrightTimeout
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise BrowserError("Playwright ist nicht installiert.") from exc
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    headless=True,
                    args=["--disable-dev-shm-usage", "--no-first-run", "--disable-extensions"],
                )
                try:
                    context = browser.new_context(locale="de-DE", service_workers="block")
                    try:
                        page = context.new_page()
                        page.set_default_timeout(self.timeout_ms)
                        self._login(page)
                        return self._read(page, "messages", MESSAGES_PATH) + self._read(
                            page, "letters", LETTERS_PATH
                        )
                    finally:
                        context.close()
                finally:
                    browser.close()
        except PlaywrightTimeout as exc:
            raise BrowserTimeout() from exc
        except BrowserError:
            raise
        except Exception as exc:
            raise BrowserError() from exc

    def _login(self, page):
        page.goto(BASE_URL, wait_until="domcontentloaded")
        page.locator('input[type="text"], input[type="email"]').first.fill(self.username)
        page.locator('input[type="password"]').first.fill(self.password)
        page.locator('button[type="submit"]').first.click()
        page.wait_for_timeout(800)
        if page.locator('input[type="password"]').first.is_visible():
            raise InvalidCredentials()

    @staticmethod
    def _read(page, kind, path):
        page.goto(BASE_URL + path, wait_until="domcontentloaded")
        rows = page.locator("[data-id], article, .message-list-item, .letter-list-item")
        items = []
        for index in range(rows.count()):
            row = rows.nth(index)
            title = row.inner_text().strip().splitlines()[0:1]
            external_id = row.get_attribute("data-id") or row.get_attribute("id") or f"row-{index}"
            if title:
                items.append(SchoolmanagerItem(kind, external_id[:128], title[0][:160]))
        return items
