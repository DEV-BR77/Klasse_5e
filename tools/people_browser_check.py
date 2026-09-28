"""Focused acceptance of people management using disposable QA accounts only."""
from datetime import date


def prepare_people():
    from klasse5e.core.models import UserAccount, Person, ClassMembership, RoleAssignment, School, SchoolClass
    primary_class = SchoolClass.objects.get(code="5e", school__slug="smoke")
    for name in ("Anna", "Zoe"):
        user, _ = UserAccount.objects.get_or_create(email=f"qa-people-{name.lower()}@example.test")
        person, _ = Person.objects.get_or_create(user=user, defaults={"first_name": name, "last_name": "Prüfperson"})
        ClassMembership.objects.get_or_create(person=person, school_class=primary_class, defaults={"valid_from": date(2026, 8, 1)})
        RoleAssignment.objects.get_or_create(user=user, role="guardian", school_class=primary_class)
    school, _ = School.objects.get_or_create(slug="qa-people-other", defaults={"name": "Andere Prüfschule"})
    other_class, _ = SchoolClass.objects.get_or_create(school=school, code="qa-other", school_year=primary_class.school_year, defaults={"name": "Andere Klasse"})
    return primary_class.school_id, primary_class.pk, other_class.pk


def check_people(page, base, width, output, fixture):
    school_id, class_id, other_class_id = fixture
    url = base + "/verwaltung/rollen/personen/"
    page.goto(url)
    content = page.locator("#main-content").bounding_box()
    assert content["width"] <= 1201 and content["x"] >= 0
    if width >= 1024:
        rail = page.locator(".app-bottom-nav").bounding_box()
        assert content["x"] >= rail["x"] + rail["width"]
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    search = page.get_by_role("searchbox")
    search.fill("Nichtvorhandene Prüfperson")
    assert page.locator('[data-live-table-empty="people-table"]').is_visible()
    search.fill("Prüfperson")
    assert page.locator('[data-table-row]:visible').count() == 2
    if width <= 768:
        mobile_sort = page.locator('[data-mobile-sort="people-table"]')
        assert mobile_sort.is_visible()
        mobile_sort.select_option("email:asc")
        assert page.locator('th[aria-sort="ascending"]').count() == 1
        assert page.locator('[data-table-row]:visible').first.get_attribute("data-sort-email").endswith("anna@example.test")
        mobile_sort.select_option("email:desc")
        assert page.locator('th[aria-sort="descending"]').count() == 1
        assert page.locator('[data-table-row]:visible').first.get_attribute("data-sort-email").endswith("zoe@example.test")
    else:
        page.locator('[data-sort-key="email"]').click()
        assert page.locator('th[aria-sort="ascending"]').count() == 1
        page.locator('[data-sort-key="email"]').click()
        assert page.locator('th[aria-sort="descending"]').count() == 1
    search.fill("Anna")
    page.locator('[name="school"]').select_option(str(school_id))
    page.locator('[name="class"]').select_option(str(class_id))
    page.locator('[name="role"]').select_option("guardian")
    page.locator('[name="status"]').select_option("active")
    page.get_by_role("button", name="Filtern", exact=True).click()
    assert page.locator('[data-table-row]').count() == 1
    page.screenshot(path=str(output / f"people-list-final-{width}.png"), full_page=True)
    page.get_by_role("link", name="Person öffnen").click()
    assert page.locator(".person-role-card").is_visible()
    assert page.locator("#people-table").count() == 0
    form = page.locator(".person-assignment-form")
    original_role = form.locator('[name="role"]').input_value()
    form.locator('[name="role"]').select_option("moderator")
    form.get_by_role("link", name="Abbrechen").click()
    assert form.locator('[name="role"]').input_value() == original_role
    form.locator('[name="role"]').select_option("editor")
    form.locator('[name="school_id"]').select_option(str(school_id))
    form.locator('[name="school_class_id"]').select_option(str(other_class_id))
    form.get_by_role("button", name="Rolle zuweisen").click()
    assert page.get_by_role("alert").first.is_visible()
    assert form.locator('[name="role"]').input_value() == "editor"
    form.locator('[name="school_class_id"]').select_option(str(class_id))
    form.get_by_role("button", name="Rolle zuweisen").click()
    page.reload()
    assignment = page.locator(".management-list li").filter(has=page.get_by_text("Redakteur", exact=True))
    assert assignment.count() == 1
    page.screenshot(path=str(output / f"people-detail-final-{width}.png"), full_page=True)
    page.once("dialog", lambda dialog: dialog.accept())
    assignment.get_by_role("button", name="Entziehen").click()
    page.reload()
    assert assignment.count() == 0
    page.locator(".page-back-navigation a").click()
    assert page.locator('[name="role"]').input_value() == "guardian"
    assert page.locator('[name="status"]').input_value() == "active"
    assert page.get_by_role("searchbox").input_value() == "Anna"
    page.get_by_role("link", name="Filter zurücksetzen").click()
    assert page.locator('[data-table-row]').count() >= 3
