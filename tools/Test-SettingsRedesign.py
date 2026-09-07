"""Isolated browser smoke check; run inside the built image, without production mounts."""

import os
import threading
from datetime import date
from pathlib import Path
from wsgiref.simple_server import make_server

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "klasse5e.settings")
os.environ["DJANGO_DEBUG"] = "1"
os.environ["DJANGO_ALLOWED_HOSTS"] = "localhost,127.0.0.1,testserver"
from django.conf import settings

settings.DATABASES["default"]["NAME"] = "/tmp/redesign-smoke.sqlite3"
settings.MEDIA_ROOT = Path("/tmp/redesign-media")
settings.SECURE_SSL_REDIRECT = False
settings.SESSION_COOKIE_SECURE = False
settings.CSRF_COOKIE_SECURE = False
import django

django.setup()
from django.core.management import call_command
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.wsgi import get_wsgi_application
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from klasse5e.core.models import (
    UserAccount,
    Person,
    SchoolYear,
    School,
    SchoolClass,
    ClassMembership,
    RoleAssignment,
)
from playwright.sync_api import sync_playwright

call_command("migrate", verbosity=0, interactive=False)
user = UserAccount.objects.create_user(email="redesign@example.test", password=None)
user.email_verified_at = timezone.now()
user.save(update_fields=["email_verified_at"])
person = Person.objects.create(user=user, first_name="Alex", last_name="Beispiel")
year = SchoolYear.objects.create(
    label="2026/27",
    starts_on=date(2026, 8, 1),
    ends_on=date(2027, 7, 31),
    is_active=True,
)
school = School.objects.create(name="Synthetische Schule", slug="smoke")
klass = SchoolClass.objects.create(
    school=school, name="Testklasse", code="5e", school_year=year
)
ClassMembership.objects.create(
    school_class=klass, person=person, valid_from=date(2026, 8, 1)
)
RoleAssignment.objects.create(user=user, school_class=klass, role="guardian")
client = Client()
client.force_login(user)
client.get(reverse("onboarding-resume"))
server = make_server("127.0.0.1", 8765, StaticFilesHandler(get_wsgi_application()))
threading.Thread(target=server.serve_forever, daemon=True).start()
output = Path("/tmp/redesign-qa")
output.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(args=["--no-sandbox"])
    context = browser.new_context()
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    base = "http://127.0.0.1:8765"
    for width in (390, 1280):
        page.set_viewport_size({"width": width, "height": 900})
        response = page.goto(base + "/accounts/login/")
        assert response.status == 200
        assert page.locator("h1").first.is_visible()
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (
            "Login overflow"
        )
        page.screenshot(path=str(output / f"login-{width}.png"), full_page=True)
    context.add_cookies(
        [
            {
                "name": settings.SESSION_COOKIE_NAME,
                "value": client.session.session_key,
                "url": base,
            }
        ]
    )
    for width in (390, 1280):
        page.set_viewport_size({"width": width, "height": 900})
        for name in (
            "onboarding-resume",
            "personal-profile",
            "ui-family",
            "ui-notifications",
            "mfa_index",
        ):
            response = page.goto(base + reverse(name))
            assert response.status == 200, (name, response.status)
            assert page.evaluate(
                "document.documentElement.scrollWidth <= innerWidth"
            ), (name, width, "overflow")
            page.screenshot(path=str(output / f"{name}-{width}.png"), full_page=True)
        page.goto(base + reverse("personal-profile"))
        page.locator("[data-avatar-open]").first.click()
        page.locator("[data-avatar-random]").click()
        page.locator("[data-avatar-apply]").click()
        assert page.locator('[name="profile_image_mode"][value="avatar"]').is_checked()
        assert page.locator("[data-avatar-seed]").input_value().startswith("v2:")
        assert not page.locator("#avatar-designer").is_visible()
    assert not errors, errors
    browser.close()
server.shutdown()
print(
    "PASS: login, setup, profile, family, notifications, MFA and avatar at 390/1280 px; no overflow or JS errors"
)
