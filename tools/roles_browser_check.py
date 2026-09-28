"""Focused browser checks for role and permission administration in the QA database."""

from datetime import date


def prepare_roles():
    from allauth.mfa.models import Authenticator
    from django.test import Client
    from klasse5e.chat.models import ChatRoom
    from klasse5e.core.models import (
        ClassMembership, Person, PortalModule, RoleAssignment, RoleModulePermission, SchoolClass, UserAccount,
    )

    school_class = SchoolClass.objects.get(code="5e", school__slug="smoke")
    user, _ = UserAccount.objects.get_or_create(email="qa-roles-guardian@example.test")
    person, _ = Person.objects.get_or_create(
        user=user, defaults={"first_name": "Robin", "last_name": "Prüfperson"},
    )
    ClassMembership.objects.get_or_create(
        person=person, school_class=school_class,
        defaults={"valid_from": date(2026, 8, 1)},
    )
    module = PortalModule.objects.get(key="chat")
    RoleModulePermission.objects.update_or_create(
        role="content_manager", module=module, action="view",
        defaults={"active": False, "scope": "class"},
    )
    RoleAssignment.objects.get_or_create(user=user, role="content_manager", school_class=school_class)
    Authenticator.objects.get_or_create(
        user=user, type=Authenticator.Type.TOTP, defaults={"data": {"secret": "synthetic-test-only"}},
    )
    for action, active in (("read", True), ("create", False)):
        RoleModulePermission.objects.update_or_create(
            role="content_manager", module=module, action=action,
            defaults={"active": active, "scope": "class"},
        )
    member_client = Client()
    member_client.force_login(user)
    room = ChatRoom.objects.get(title="Smoke-Elternchat")
    return user.pk, user.email, school_class.pk, module.pk, room.pk, member_client.session.session_key


def check_roles(page, base, width, output, fixture):
    user_id, email, class_id, module_id, room_id, member_session = fixture
    management_url = base + "/verwaltung/rollen/"
    permissions_url = base + "/verwaltung/rollen/berechtigungen/?role=content_manager"

    page.goto(management_url)
    assert page.get_by_role("heading", name="Rollenverwaltung", exact=True).is_visible()
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    role_form = page.locator('form:has(input[name="form"][value="role"])')
    role_form.locator('select[name="user"]').select_option(str(user_id))
    role_form.locator('select[name="role"]').select_option("parent_representative")
    role_form.get_by_role("button", name="Rolle speichern").click()
    assert page.get_by_text("Elternvertretungen benötigen einen aktiven Zugang").is_visible()
    role_form.locator('select[name="school_class"]').select_option(str(class_id))
    role_form.get_by_role("button", name="Rolle speichern").click()
    row = page.locator(".management-list li").filter(has_text=email).filter(has_text="Elternvertretung")
    assert row.count() == 1
    page.screenshot(path=str(output / f"role-management-final-{width}.png"), full_page=True)
    page.once("dialog", lambda dialog: dialog.accept())
    row.get_by_role("button", name="Entziehen").click()
    assert page.locator(".management-list li").filter(has_text=email).count() == 0

    room_panel = page.locator("section.settings-panel").filter(
        has=page.get_by_role("heading", name="Elternvertreter-Chat")
    )
    room_panel.locator('select[name="room"]').select_option(str(room_id))
    room_panel.locator('input[name="enabled"]').check()
    room_panel.get_by_role("button", name="Chatzuordnung speichern").click()
    assert room_panel.locator(".management-list").get_by_text("Smoke-Elternchat").is_visible()
    room_panel.locator('select[name="room"]').select_option(str(room_id))
    room_panel.get_by_role("button", name="Chatzuordnung speichern").click()
    assert room_panel.locator(".management-list").get_by_text("Noch kein Chat ausgewählt.").is_visible()

    page.goto(permissions_url)
    assert page.get_by_role("heading", name="Rollenberechtigungen", exact=True).is_visible()
    module = page.locator(".permission-card").filter(has=page.locator("summary strong", has_text="Chat"))
    module.locator("summary").click()
    checkbox = module.locator(f'input[name="permission-{module_id}-view"]')
    scope = module.locator(f'select[name="scope-{module_id}-view"]')
    assert not checkbox.is_checked()
    checkbox.check()
    scope.select_option("own")
    assert module.get_by_text("Sichtbar", exact=True).is_visible()
    page.evaluate("scrollTo(0, 0)")
    page.screenshot(path=str(output / f"role-permissions-final-{width}.png"), full_page=True)
    page.get_by_role("button", name="Berechtigungen speichern").click()
    module.locator("summary").click()
    assert checkbox.is_checked() and scope.input_value() == "own"
    scope.select_option("school")
    page.get_by_role("link", name="Abbrechen", exact=True).click()
    module.locator("summary").click()
    assert scope.input_value() == "own"
    checkbox.uncheck()
    page.get_by_role("button", name="Berechtigungen speichern").click()
    module.locator("summary").click()
    assert not checkbox.is_checked() and scope.input_value() == "own"
    page.locator('.role-selector__item[href="?role=editor"]').click()
    assert page.get_by_role("heading", name="Redakteur", exact=True).is_visible()
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")

    # Verify the downstream UI using a separate real user session. Changing
    # the matrix must change the available chat action on the next request.
    from django.conf import settings
    page.goto(permissions_url)
    module.locator("summary").click()
    checkbox.check()
    scope.select_option("class")
    create = module.locator(f'input[name="permission-{module_id}-create"]')
    create.uncheck()
    page.get_by_role("button", name="Berechtigungen speichern").click()
    member_context = page.context.browser.new_context(viewport={"width": width, "height": 900})
    member_context.add_cookies([{"name": settings.SESSION_COOKIE_NAME, "value": member_session, "url": base}])
    member_page = member_context.new_page()
    member_page.goto(base + "/chat/")
    assert member_page.get_by_role("heading", name="Chat", exact=True).is_visible()
    assert member_page.get_by_role("button", name="Neuen Raum anlegen").count() == 0
    module.locator("summary").click()
    create.check()
    page.get_by_role("button", name="Berechtigungen speichern").click()
    member_page.reload()
    assert member_page.get_by_role("button", name="Neuen Raum anlegen").is_visible()
    assert member_page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    member_page.screenshot(path=str(output / f"role-effect-chat-{width}.png"), full_page=True)
    module.locator("summary").click()
    create.uncheck()
    checkbox.uncheck()
    page.get_by_role("button", name="Berechtigungen speichern").click()
    member_page.reload()
    assert member_page.get_by_role("button", name="Neuen Raum anlegen").count() == 0
    member_context.close()
