"""Narrow, UI-only Playwright transport for a WebUntis absence form.

It is purpose-built for the school-approved THG WebUntis host.  It never uses
the internal JSON API and never retries the one external write.
"""

import re
from datetime import datetime
from urllib.parse import urlparse

from .absence_verification import AbsenceRecord
from .browser_homework import BrowserCrashed, BrowserTimeout
from .client import ALLOWED_HOST, InvalidCredentials

LOGIN_PATH = "/WebUntis/"
ABSENCES_PATH = "/student-absences"


def _allowed_url(url, path):
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname == ALLOWED_HOST and parsed.port is None and parsed.path == path


class PlaywrightAbsenceClient:
    def __init__(self, username, password, *, server=ALLOWED_HOST, school="thgwob", student_key="", timeout_ms=30_000):
        if server != ALLOWED_HOST or not student_key:
            raise ValueError("WebUntis-Ziel oder Kindbindung nicht freigegeben")
        self.username = username
        self.password = password
        self.server = server
        self.school = school
        self.student_key = str(student_key)
        self.timeout_ms = min(max(int(timeout_ms), 5_000), 45_000)
        self._playwright = self._browser = self._context = self._page = None

    def __enter__(self):
        try:
            from playwright.sync_api import TimeoutError as PlaywrightTimeout
            from playwright.sync_api import sync_playwright

            self._timeout_error = PlaywrightTimeout
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=True, args=["--disable-dev-shm-usage", "--no-first-run", "--disable-extensions"]
            )
            self._context = self._browser.new_context(
                locale="de-DE", service_workers="block", viewport={"width": 1024, "height": 768}
            )
            self._page = self._context.new_page()
            self._page.set_default_timeout(self.timeout_ms)
            self._page.route(
                "**/*",
                lambda route: route.abort() if route.request.resource_type in {"image", "media", "font"} else route.continue_(),
            )
            self._login()
            return self
        except Exception as exc:
            self.__exit__(None, None, None)
            if isinstance(exc, getattr(self, "_timeout_error", ())):
                raise BrowserTimeout() from exc
            if isinstance(exc, ValueError | InvalidCredentials):
                raise
            raise BrowserCrashed() from exc

    def __exit__(self, _type, _value, _traceback):
        for resource in (self._context, self._browser, self._playwright):
            if resource is not None:
                try:
                    resource.close() if resource is self._context or resource is self._browser else resource.stop()
                except Exception:
                    pass

    def _login(self):
        url = f"https://{self.server}{LOGIN_PATH}?school={self.school}#/basic/login"
        if not _allowed_url(url, LOGIN_PATH):
            raise ValueError("Nicht freigegebener WebUntis-Login")
        self._page.goto(url, wait_until="domcontentloaded")
        self._page.locator('input[type="text"]').first.fill(self.username)
        password = self._page.locator('input[type="password"]').first
        password.fill(self.password)
        self._page.locator('button[type="submit"]').first.click()
        self._page.wait_for_timeout(1_000)
        if password.is_visible():
            raise InvalidCredentials()

    def _frame(self):
        url = f"https://{self.server}{ABSENCES_PATH}"
        if not _allowed_url(url, ABSENCES_PATH):
            raise ValueError("Nicht freigegebene WebUntis-Abwesenheitsseite")
        self._page.goto(url, wait_until="domcontentloaded")
        self._page.locator("#embedded-webuntis").wait_for(state="attached")
        return self._page.frame_locator("#embedded-webuntis")

    @staticmethod
    def _date_time(value):
        return datetime.strptime(value, "%d.%m.%Y %H:%M")

    def read_absences(self):
        frame = self._frame()
        rows = frame.locator("tbody tr")
        rows.first.wait_for(state="attached") if rows.count() else None
        records = []
        for index in range(rows.count()):
            row = rows.nth(index)
            cells = row.locator("td")
            if cells.count() < 5:
                continue
            start_value = cells.nth(0).inner_text().strip()
            end_value = cells.nth(1).inner_text().strip()
            if not re.fullmatch(r"\d{1,2}\.\d{1,2}\.\d{4}\s+\d{1,2}:\d{2}", start_value) or not re.fullmatch(r"\d{1,2}\.\d{1,2}\.\d{4}\s+\d{1,2}:\d{2}", end_value):
                continue
            try:
                records.append(
                    AbsenceRecord(
                        self.student_key,
                        self._date_time(start_value),
                        self._date_time(end_value),
                        cells.nth(4).inner_text().strip(),
                        row.get_attribute("data-id") or row.get_attribute("data-row-key") or "",
                    )
                )
            except ValueError:
                continue
        return records

    def prepare_absence(self, expected):
        frame = self._page.frame_locator("#embedded-webuntis")
        frame.get_by_role("button", name="Abwesenheit melden").click()
        dialog = frame.locator('[role="dialog"]').last
        dialog.wait_for(state="visible")
        fields = dialog.locator('input[type="text"]')
        if fields.count() < 3:
            raise ValueError("WebUntis-Meldeformular unvollständig")
        fields.nth(0).fill(expected.starts_at.strftime("%d.%m.%Y %H:%M"))
        fields.nth(1).fill(expected.ends_at.strftime("%d.%m.%Y %H:%M"))
        fields.nth(2).fill(expected.note)

    def submit_absence(self):
        dialog = self._page.frame_locator("#embedded-webuntis").locator('[role="dialog"]').last
        dialog.get_by_role("button", name="Speichern").click()
        dialog.wait_for(state="hidden")
