"""Isolated browser smoke check; run inside the built image, without production mounts."""

# Django must be configured before importing model-dependent modules.
# ruff: noqa: E402

import os
import threading
import tempfile
import json
from datetime import date
from pathlib import Path
from wsgiref.simple_server import make_server, WSGIRequestHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "klasse5e.settings")
os.environ["DJANGO_DEBUG"] = "1"
os.environ["DJANGO_ALLOWED_HOSTS"] = "localhost,127.0.0.1,testserver"
os.environ["TEMPORARY_ADMIN_MFA_BYPASS"] = "1"
from django.conf import settings

run_directory = tempfile.TemporaryDirectory(prefix="klassid-redesign-")
qa_db = os.environ.get("REDESIGN_QA_DB")
if qa_db and not qa_db.startswith("/tmp/klassid-qa-"):
    raise RuntimeError("Only an isolated /tmp/klassid-qa- database is allowed")
settings.DATABASES["default"]["NAME"] = qa_db or str(Path(run_directory.name) / "browser.sqlite3")
settings.MEDIA_ROOT = Path(run_directory.name) / "media"
settings.SECURE_SSL_REDIRECT = False
settings.SESSION_COOKIE_SECURE = False
settings.CSRF_COOKIE_SECURE = False
import django

django.setup()
from django.core.management import call_command
from django.db import connections
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
    GuardianChildRelationship,
    StudentProfile,
)
from klasse5e.chat.models import ChatAsset, ChatMessage, ChatRoom
from playwright.sync_api import sync_playwright

if not Path(settings.DATABASES["default"]["NAME"]).exists():
    call_command("migrate", verbosity=0, interactive=False)
    user = UserAccount.objects.create_user(email="redesign@example.test", password=None)
    user.email_verified_at = timezone.now()
    user.is_superuser = True
    user.is_staff = True
    user.save(update_fields=["email_verified_at", "is_superuser", "is_staff"])
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
    child_person = Person.objects.create(first_name="Mila", last_name="Beispiel")
    StudentProfile.objects.create(person=child_person)
    ClassMembership.objects.create(
        school_class=klass, person=child_person, valid_from=date(2026, 8, 1)
    )
    child_relationship = GuardianChildRelationship.objects.create(
        guardian_person=person,
        student_person=child_person,
        relationship_type="guardian",
        is_legal_guardian=True,
        may_view_student_profile=True,
        may_manage_profile=True,
        may_manage_general_consents=True,
        may_manage_photo_consents=True,
        valid_from=date(2026, 8, 1),
        status="verified",
        verified_by=user,
        verified_at=timezone.now(),
    )
    RoleAssignment.objects.create(user=user, school_class=klass, role="guardian")
    RoleAssignment.objects.create(user=user, school=school, role="primary_admin")
    ChatAsset.objects.get_or_create(
        kind="sticker",
        label="Smoke-Sticker",
        defaults={"value": "smoke-sticker", "is_active": True, "sort_order": 1},
    )
    chat_room = ChatRoom.objects.create(
        school_class=klass,
        school_year=year,
        title="Smoke-Elternchat",
        appearance="modern",
    )
    ChatMessage.objects.create(room=chat_room, author=user, body="Smoke-Nachricht")
else:
    user = UserAccount.objects.get(email="redesign@example.test")
    child_relationship = GuardianChildRelationship.objects.get(guardian_person=user.person)
    chat_room = ChatRoom.objects.get(title="Smoke-Elternchat")
client = Client()
client.force_login(user)
client.get(reverse("onboarding-resume"))
class QuietHandler(WSGIRequestHandler):
    def log_message(self, *_args):
        pass

server = make_server("127.0.0.1", 0, StaticFilesHandler(get_wsgi_application()), handler_class=QuietHandler)
server_thread = threading.Thread(target=server.serve_forever, daemon=True)
server_thread.start()
output = Path(
    os.environ.get(
        "REDESIGN_QA_OUTPUT",
        Path(__file__).resolve().parents[1] / "qa-artifacts" / "redesign-current",
    )
)
output.mkdir(parents=True, exist_ok=True)
focus = os.environ.get("REDESIGN_QA_FOCUS", "")
if focus == "people":
    from people_browser_check import prepare_people, check_people
    people_fixture = prepare_people()
elif focus == "roles":
    from roles_browser_check import prepare_roles, check_roles
    roles_fixture = prepare_roles()
elif focus == "chat":
    from chat_browser_check import prepare_chat, check_chat
    chat_fixture = prepare_chat()
elif focus == "avatar":
    from avatar_browser_check import check_avatar
    avatar_fixture = {"relationship_id": child_relationship.pk}
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", args=["--no-sandbox"])
    context = browser.new_context()
    page = context.new_page()
    errors = []
    layout_errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    base = f"http://127.0.0.1:{server.server_port}"
    for width in (() if focus else (360, 768, 1440)):
        page.set_viewport_size({"width": width, "height": 900})
        response = page.goto(base + "/accounts/login/")
        assert response.status == 200
        assert page.locator("h1").first.is_visible()
        assert page.evaluate(
            "document.documentElement.scrollWidth <= innerWidth"
        ), (
            "Login overflow"
        )
        page.screenshot(path=str(output / f"login-{width}.png"), full_page=False)
    context.add_cookies(
        [
            {
                "name": settings.SESSION_COOKIE_NAME,
                "value": client.session.session_key,
                "url": base,
            }
        ]
    )
    for width in ((360, 768, 1440, 1920) if focus else (360, 768, 1440)):
        page.set_viewport_size({"width": width, "height": 900})
        if focus == "people":
            check_people(page, base, width, output, people_fixture)
            continue
        if focus == "roles":
            check_roles(page, base, width, output, roles_fixture)
            continue
        if focus == "chat":
            check_chat(page, base, width, output, chat_fixture)
            continue
        if focus == "avatar":
            check_avatar(page, base, width, output, avatar_fixture)
            continue
        page.goto(base + reverse("dashboard"))
        context_menu = page.locator(".app-child-context")
        heading_top = page.locator("h1").first.bounding_box()["y"]
        context_menu.locator("summary").click()
        assert context_menu.locator("nav").is_visible()
        panel_box = context_menu.locator("nav").bounding_box()
        assert panel_box["y"] >= 0 and panel_box["y"] + panel_box["height"] <= 900
        assert abs(page.locator("h1").first.bounding_box()["y"] - heading_top) < 1
        page.screenshot(path=str(output / f"family-context-{width}.png"), full_page=False)
        page.keyboard.press("Escape")
        assert not context_menu.locator("nav").is_visible()
        context_menu.locator("summary").click()
        context_menu.get_by_role("button", name="Mila", exact=True).click()
        assert page.locator(".app-child-context__label").inner_text() == "Mila"
        page.locator(".app-child-context > summary").click()
        page.locator(".app-child-context").get_by_role("button", name="Alle Kinder").click()
        assert page.locator(".app-child-context__label").inner_text() == "Alle Kinder"
        page.goto(base + reverse("ui-more") + "?bereich=einstellungen")
        design_section = page.locator(".portal-directory__section").filter(
            has=page.locator("summary", has_text="Design")
        )
        design_section.locator("summary").click()
        page.locator("h1").click()
        assert design_section.get_attribute("open") is not None
        for name in (
            "dashboard",
            "ui-calendar",
            "ui-contacts",
            "ui-documents",
            "ui-chat",
            "ui-more",
            "onboarding-resume",
            "personal-profile",
            "ui-family",
            "ui-notifications",
            "mfa_index",
            "portal-management",
            "school-management",
            "role-people",
            "role-permissions",
            "theme-management",
            "monitoring-dashboard",
            "design-system",
            "role-management",
            "menu-management",
            "session-timeout-settings",
            "chat-retention-settings",
            "chat-assets-settings",
            "portal-adapter-management",
            "pilot-reports-management",
            "registration-invitation",
            "family-invitations",
            "ui-learning-portals",
            "ui-posts",
            "ui-events",
            "ui-teachers",
            "ui-galleries",
            "meal-plans",
            "ui-consents",
            "ui-system-status",
            "webuntis-calendar-settings",
        ):
            response = page.goto(base + reverse(name))
            assert response.status == 200, (name, response.status)
            page.evaluate("window.scrollTo(0, 0)")
            if name != "mfa_index":
                assert "/accounts/2fa/" not in page.url, (name, page.url)
                assert page.locator("h1").first.is_visible(), (name, "missing h1")
            page.screenshot(path=str(output / f"{name}-{width}.png"), full_page=False)
            if not page.evaluate("document.documentElement.scrollWidth <= innerWidth"):
                layout_errors.append((name, width, "overflow"))
            if name == "role-people":
                page.get_by_role("link", name="Person öffnen", exact=True).first.click()
                assert page.locator(".person-role-card").is_visible()
                assert page.locator(".person-assignment-form").is_visible()
                assert page.locator("#people-table").count() == 0
                page.screenshot(path=str(output / f"person-detail-{width}.png"), full_page=False)
                page.locator(".page-back-navigation a").click()
                assert page.locator("#people-table").is_visible()
            if name == "personal-profile":
                original_name = page.locator('input[name="first_name"]').input_value()
                page.locator('input[name="first_name"]').fill("Nicht gespeicherter Entwurf")
                page.locator("#main-content .form-actions").get_by_role("link", name="Abbrechen", exact=True).click()
                assert page.locator('input[name="first_name"]').input_value() == original_name
            if name == "theme-management":
                edit_button = page.locator('[data-dialog-open^="edit-theme-"]').first
                assert edit_button.is_visible(), (name, "missing edit action")
                edit_button.click()
                edit_dialog = page.locator('dialog[id^="edit-theme-"]').first
                assert edit_dialog.is_visible(), (name, "edit dialog did not open")
                edit_dialog.locator('input[name="description"]').fill("Smoke-Update des Designs")
                edit_dialog.locator('[name="shadow_strength"]').evaluate(
                    "el => { el.type = 'text'; el.value = '100'; }"
                )
                edit_dialog.get_by_role("button", name="Änderungen speichern").click()
                assert page.locator('#main-content [name="description"]').input_value() == "Smoke-Update des Designs"
                assert page.locator(".errorlist").is_visible()
                page.locator('[name="shadow_strength"]').fill("10")
                page.get_by_role("button", name="Änderungen speichern", exact=True).click()
                assert page.get_by_text("wurde aktualisiert.", exact=False).first.is_visible()
        page.goto(base + reverse("personal-profile") + "?tab=themes")
        original_theme = page.locator("html").get_attribute("data-theme")
        original_style = page.locator("html").get_attribute("style")
        preview_buttons = page.locator("[data-theme-preview]")
        for index in range(preview_buttons.count()):
            button = preview_buttons.nth(index)
            key = button.get_attribute("data-theme-key")
            button.click()
            assert page.locator("html").get_attribute("data-theme") == key
            assert page.locator("[data-theme-preview-bar]").is_visible()
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (key, width)
            page.screenshot(path=str(output / f"theme-{key}-{width}.png"), full_page=False)
            page.locator("[data-theme-preview-cancel]").click()
            assert page.locator("html").get_attribute("style") == original_style
            assert page.locator("html").get_attribute("data-theme") == original_theme
        preview_buttons.first.click()
        applied_key = preview_buttons.first.get_attribute("data-theme-key")
        page.locator("[data-theme-preview-bar]").get_by_role("button", name="Übernehmen").click()
        page.reload()
        assert page.locator("html").get_attribute("data-theme") == applied_key
        assert not page.locator("[data-theme-preview-bar]").is_visible()
        page.goto(base + reverse("design-system"))
        editor = page.locator("[data-token-editor]")
        editor.locator('[name="primary"]').fill("#345678")
        assert editor.locator("[data-token-specimen]").evaluate(
            "el => getComputedStyle(el).getPropertyValue('--color-primary').trim()"
        ) == "#345678"
        editor.get_by_role("button", name="Design-Tokens speichern", exact=True).click()
        page.reload()
        assert page.locator('[data-token-editor] [name="primary"]').input_value() == "#345678"
        page.goto(base + reverse("chat-assets-settings"))
        asset_trigger = page.locator('[data-dialog-open^="edit-chat-asset-"]').first
        asset_dialog_id = asset_trigger.get_attribute("data-dialog-open")
        asset_trigger.click()
        asset_dialog = page.locator("#" + asset_dialog_id)
        original_asset_label = asset_dialog.locator('[name="label"]').input_value()
        asset_dialog.locator('[name="label"]').fill("Verworfener Entwurf")
        asset_dialog.get_by_role("button", name="Abbrechen", exact=True).click()
        assert not asset_dialog.is_visible()
        assert page.locator('[data-dialog-open="' + asset_dialog_id + '"]').evaluate("el => el === document.activeElement")
        page.locator('[data-dialog-open="' + asset_dialog_id + '"]').click()
        assert asset_dialog.locator('[name="label"]').input_value() == original_asset_label
        asset_dialog.locator('[name="sort_order"]').evaluate("el => { el.type = 'text'; el.value = 'ungueltig'; }")
        asset_dialog.get_by_role("button", name="Speichern", exact=True).click()
        page.locator(".errorlist").first.wait_for()
        assert page.locator('.main-content [name="label"]').input_value() == original_asset_label
        page.screenshot(path=str(output / f"chat-asset-validation-{width}.png"), full_page=True)
        page.locator('.main-content [name="sort_order"]').fill("4")
        page.get_by_role("button", name="Speichern", exact=True).click()
        page.locator('[data-dialog-open="' + asset_dialog_id + '"]').click()
        assert asset_dialog.locator('[name="sort_order"]').input_value() == "4"
        assert asset_dialog.evaluate("el => !el.closest('table')")
        checkbox_box = asset_dialog.locator('[name="is_active"]').bounding_box()
        assert checkbox_box["width"] <= 24 and checkbox_box["height"] <= 24, checkbox_box
        page.screenshot(path=str(output / f"chat-asset-editor-{width}.png"), full_page=False)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), ("chat-assets-settings", width)
        page.keyboard.press("Escape")
        page.goto(base + reverse("monitoring-dashboard"))
        page.locator('[name="warning_threshold_percent"]').fill("75")
        page.locator('[name="critical_threshold_percent"]').fill("92")
        page.locator('[name="retention_days"]').fill("45")
        page.get_by_role("button", name="Monitoring speichern").click()
        assert page.locator("#monitoring-config-heading").is_visible()
        for family_tab in ("data", "privacy", "modules"):
            family_response = page.goto(
                base
                + reverse("ui-family")
                + f"?tab={family_tab}&child={child_relationship.pk}"
            )
            assert family_response.status == 200
            assert page.locator("#family-page-title").is_visible()
            assert page.get_by_text("Mila verwalten", exact=True).first.is_visible()
            assert page.evaluate(
                "document.documentElement.scrollWidth <= innerWidth"
            ), ("ui-family", family_tab, width, "overflow")
        room_response = page.goto(
            base + reverse("ui-chat-room", kwargs={"room_id": chat_room.public_id})
        )
        assert room_response.status == 200
        page.evaluate("window.scrollTo(0, 0)")
        assert page.locator(".conversation-list").is_visible() == (width > 768)
        assert page.locator(".conversation-list .conversation-row").count() >= 1
        assert page.locator("#chat-room-heading").is_visible()
        assert page.get_by_text("Smoke-Nachricht", exact=True).is_visible()
        assert page.locator("[data-chat-file]").count() == 1
        assert page.locator("[data-emoji-toggle]").is_visible()
        page.locator(".message-row").first.focus()
        page.locator(".message-row").first.hover()
        page.locator(".message-menu > summary").first.click()
        report = page.locator(".message-report").first
        assert report.count() == 1
        assert report.get_attribute("open") is None
        report.locator("summary").click()
        assert report.locator("summary", has_text="Melden").is_visible()
        assert report.locator(".message-report__form button", has_text="Meldung senden").is_visible()
        assert page.locator(".message-action--danger").first.is_visible()
        assert report.locator(".message-report__form select[name=reason]").is_visible()
        page.locator(".message-menu > summary").first.click()
        page.locator("[data-emoji-toggle]").click()
        assert page.locator("[data-emoji-picker]").is_visible()
        page.locator("[data-emoji-toggle]").click()
        page.locator("[data-sticker-toggle]").click()
        assert page.locator("[data-sticker-picker]").is_visible()
        page.evaluate("window.scrollTo(0, 0)")
        page.screenshot(path=str(output / f"ui-chat-room-{width}.png"), full_page=False)
        assert page.evaluate(
            "document.documentElement.scrollWidth <= innerWidth"
        ), ("ui-chat-room", width, "overflow")
        page.keyboard.press("Escape")
        draft = f"Browser-Prüfung {Path(run_directory.name).name} {width}"
        composer = page.locator("[data-chat-composer]")
        composer.locator("textarea").fill(draft)
        room_url = page.url
        def reject_send(route):
            if route.request.method == "POST":
                route.abort()
            else:
                route.continue_()
        page.route(room_url, reject_send)
        composer.get_by_role("button", name="Nachricht senden").click()
        page.wait_for_function("document.querySelector('[data-composer-status]').textContent.length > 0 && !document.querySelector('.send-button').disabled")
        assert composer.locator("textarea").input_value() == draft
        page.unroute(room_url, reject_send)
        composer.get_by_role("button", name="Nachricht senden").click()
        page.get_by_text(draft, exact=True).wait_for()
        row = page.locator(".message-row").filter(has=page.get_by_text(draft, exact=True))
        row.locator(".message-menu > summary").click()
        row.locator("[data-message-edit-open]").click()
        edit = page.locator("#edit-chat-message")
        edit.locator("textarea").fill(draft + " korrigiert")
        edit.get_by_role("button", name="Speichern", exact=True).click()
        page.get_by_text(draft + " korrigiert", exact=True).wait_for()
        page.reload()
        assert page.get_by_text(draft + " korrigiert", exact=True).is_visible()
        page.goto(base + reverse("personal-profile") + "?tab=appearance")
        page.locator("[data-avatar-open]").first.click()
        assert page.locator('[data-avatar-panel="pose"]').is_visible()
        for pose in (0, 1):
            page.locator(f'[data-avatar-option="pose"][data-avatar-index="{pose}"]').click()
            page.screenshot(path=str(output / f"avatar-pose-{pose}-{width}.png"), full_page=False)
        random_button = page.locator("[data-avatar-random]")
        random_button.scroll_into_view_if_needed()
        random_button.click()
        apply_button = page.locator("[data-avatar-apply]")
        apply_button.scroll_into_view_if_needed()
        apply_button.click()
        assert page.locator('[name="profile_image_mode"]').input_value() == "avatar"
        assert page.locator("[data-avatar-seed]").input_value().startswith("v3:")
        assert not page.locator("#avatar-designer").is_visible()
    (output / "browser-errors.json").write_text(json.dumps(errors, indent=2))
    assert not errors, errors
    assert not layout_errors, layout_errors
    browser.close()
server.shutdown()
server.server_close()
server_thread.join(timeout=5)
connections.close_all()
run_directory.cleanup()
print(
    "PASS: people management at 360/768/1440/1920 px" if focus == "people" else
    "PASS: role and permission management at 360/768/1440/1920 px" if focus == "roles" else
    "PASS: chat room, membership, message, attachment and moderation clicks at 360/768/1440/1920 px" if focus == "chat" else
    "PASS: avatar poses, cancel/save/reopen and profile subpages at 360/768/1440/1920 px" if focus == "avatar" else
    "PASS: responsive portal, chat actions, emoji/sticker pickers, settings and avatar at 360/768/1440 px; no overflow or JS errors"
)
