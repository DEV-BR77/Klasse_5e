"""Sanitized browser-only homework reference; not used by production."""

import json
import os
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


def required(name):
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def main():
    target = required("WEBUNTIS_HOMEWORK_URL")
    if urlparse(target).hostname != "thgwob.webuntis.com":
        raise RuntimeError("Unexpected WebUntis host")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(target, wait_until="domcontentloaded")
        page.get_by_label("Benutzername").fill(required("WEBUNTIS_USERNAME"))
        page.get_by_label("Passwort").fill(required("WEBUNTIS_PASSWORD"))
        page.get_by_role("button", name="Login").click()
        page.wait_for_load_state("networkidle")
        rows = [
            text.strip()
            for text in page.locator("main").all_inner_texts()
            if text.strip()
        ]
        output = os.environ.get("WEBUNTIS_OUTPUT", "homework.json")
        with open(output, "w", encoding="utf-8") as stream:
            json.dump({"captured_text": rows}, stream, ensure_ascii=False, indent=2)
        browser.close()


if __name__ == "__main__":
    main()
