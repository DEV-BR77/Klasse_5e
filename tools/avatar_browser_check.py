"""Synthetic browser acceptance for the profile avatar and nearby account pages."""


def _check_dialog(page, width, output, open_label):
    form = page.locator("form").filter(has=page.locator("[data-avatar-seed]")).first
    original = form.locator("[data-avatar-seed]").input_value()
    form.get_by_role("button", name=open_label).click()
    dialog = page.locator("#avatar-designer")
    assert dialog.is_visible()
    assert dialog.locator('[data-avatar-category="pose"]').get_attribute("aria-selected") == "true"
    assert dialog.locator('[data-avatar-options="pose"] .avatar-option').count() == 2
    assert dialog.evaluate("element => { const r = element.getBoundingClientRect(); return r.left >= 0 && r.right <= innerWidth && r.top >= 0 && r.bottom <= innerHeight; }")
    assert dialog.locator(".dialog-actions").evaluate("element => { const r = element.getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight; }")
    assert dialog.get_by_role("button", name="Übernehmen").evaluate("element => element.scrollWidth <= element.clientWidth")
    sitting = dialog.locator('[data-avatar-option="pose"][data-avatar-index="1"]')
    sitting.click()
    assert sitting.get_attribute("aria-pressed") == "true"
    assert "pose/sitting" in dialog.locator("[data-avatar-preview] image").first.get_attribute("href")
    dialog.get_by_role("tab", name="Kleidung").click()
    dialog.locator('[data-avatar-option="body"][data-avatar-index="1"]').click()
    dialog.get_by_role("tab", name="Hintergrund").click()
    dialog.locator('[data-avatar-option="background"][data-avatar-index="2"]').click()
    page.screenshot(path=str(output / f"avatar-dialog-{width}.png"), full_page=False)
    dialog.get_by_role("button", name="Abbrechen").click()
    assert not dialog.is_visible()
    assert form.locator("[data-avatar-seed]").input_value() == original
    form.get_by_role("button", name=open_label).click()
    dialog.locator('[data-avatar-option="pose"][data-avatar-index="1"]').click()
    dialog.get_by_role("button", name="Übernehmen").click()
    assert not dialog.is_visible()
    assert form.locator("[data-avatar-seed]").input_value().startswith("v3:0:1:")
    assert "pose/sitting" in form.locator("[data-profile-current-preview] image").first.get_attribute("href")
    return form


def check_avatar(page, base, width, output, fixture):
    response = page.goto(base + "/einstellungen/profil/?tab=appearance")
    assert response.status == 200
    form = _check_dialog(page, width, output, "Avatar verwenden")
    form.get_by_role("button", name="Profilbild speichern").click()
    assert "tab=appearance" in page.url
    saved = page.locator(".profile-image-form [data-avatar-seed]").input_value()
    assert saved.startswith("v3:0:1:")
    assert "pose/sitting" in page.locator(".profile-image-form [data-profile-current-preview] image").first.get_attribute("href")
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.screenshot(path=str(output / f"avatar-profile-{width}.png"), full_page=False)

    if width == 360:
        response = page.goto(base + f"/mehr/familie/?tab=data&child={fixture['relationship_id']}")
        assert response.status == 200
        form = _check_dialog(page, width, output, "Avatar gestalten")
        form.get_by_role("button", name="Angaben speichern").click()
        assert "tab=data" in page.url
        assert page.locator('[data-avatar-seed]').input_value().startswith("v3:0:1:")
        assert "pose/sitting" in page.locator("[data-profile-current-preview] image").first.get_attribute("href")
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.locator("[data-profile-current-preview]").scroll_into_view_if_needed()
        page.screenshot(path=str(output / "avatar-child-360.png"), full_page=False)

    for tab, heading in (("data", "Stammdaten"), ("themes", "Design & Themes"),
                         ("notifications", "Benachrichtigungen"), ("app", "KlassID als App installieren"),
                         ("account", "Sicherheit")):
        response = page.goto(base + f"/einstellungen/profil/?tab={tab}")
        assert response.status == 200
        assert page.get_by_text(heading, exact=False).first.is_visible()
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), tab
    if width == 360:
        page.goto(base + "/einstellungen/profil/?tab=data")
        data_form = page.locator(".settings-page form").first
        original_name = data_form.locator('[name="chat_display_name"]').input_value()
        data_form.locator('[name="chat_display_name"]').fill("Entwurf ohne Speichern")
        data_form.get_by_role("link", name="Abbrechen").click()
        assert page.locator('[name="chat_display_name"]').input_value() == original_name
        page.locator('[name="chat_display_name"]').fill("Browser-Profilname")
        page.get_by_role("button", name="Angaben speichern").click()
        assert page.locator('[name="chat_display_name"]').input_value() == "Browser-Profilname"

        page.goto(base + "/einstellungen/profil/?tab=notifications")
        preferences = page.locator(".settings-page form").first
        setting = preferences.locator('[data-notification-channel="inapp"]').first
        original = setting.is_checked()
        setting.locator("..").click()
        assert setting.is_checked() is not original
        preferences.get_by_role("button", name="Einstellungen speichern").click()
        assert page.locator('[data-notification-channel="inapp"]').first.is_checked() is not original
    page.screenshot(path=str(output / f"profile-small-pages-{width}.png"), full_page=False)
