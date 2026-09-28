"""End-to-end clicks for the local, synthetic chat acceptance fixture."""

import uuid
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from PIL import Image

from klasse5e.chat.models import ChatAsset
from klasse5e.core.models import ClassMembership, Person, SchoolClass, UserAccount


def prepare_chat():
    school_class = SchoolClass.objects.get(code="5e")
    candidate, _ = UserAccount.objects.get_or_create(
        email="chat-browser-member@example.test",
        defaults={"email_verified_at": timezone.now()},
    )
    person, _ = Person.objects.get_or_create(
        user=candidate,
        defaults={"first_name": "Mira", "last_name": "Browser"},
    )
    ClassMembership.objects.get_or_create(
        school_class=school_class,
        person=person,
        defaults={"valid_from": school_class.school_year.starts_on},
    )
    image = BytesIO()
    Image.new("RGBA", (64, 64), (255, 190, 0, 255)).save(image, format="PNG")
    asset, _ = ChatAsset.objects.get_or_create(
        kind=ChatAsset.Kind.STICKER,
        label="Browser-Grafiksticker",
        defaults={
            "value": "", "is_active": True,
            "image": SimpleUploadedFile("browser-sticker.png", image.getvalue(), content_type="image/png"),
        },
    )
    if not asset.image or not asset.image.storage.exists(asset.image.name):
        asset.image.save(
            f"browser-sticker-{uuid.uuid4().hex}.png",
            SimpleUploadedFile("browser-sticker.png", image.getvalue(), content_type="image/png"),
        )
    return {"member_id": candidate.pk, "sticker_id": asset.pk}


def check_chat(page, base, width, output, fixture):
    if width == 360:
        page.on("dialog", lambda dialog: dialog.accept())
    response = page.goto(base + "/chat/")
    assert response.status == 200
    page.get_by_role("button", name="Neuen Raum anlegen").click()
    new_room = page.locator("#new-chat-room")
    assert new_room.is_visible()
    title = f"Browser-Chat {width}-{uuid.uuid4().hex[:6]}"
    new_room.locator('input[name="title"]').fill(title)
    new_room.get_by_role("button", name="Anlegen").click()
    row = page.locator(".conversation-row-wrap").filter(has_text=title)
    row.locator(".conversation-row").click()
    assert page.locator("#chat-room-heading").inner_text() == title
    room_url = page.url
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")

    panel = page.locator(".chat-members-panel")
    panel.locator("summary").click()
    panel.locator('form.chat-member-form select[name="user_id"]').select_option(str(fixture["member_id"]))
    panel.locator('form.chat-member-form select[name="role"]').select_option("moderator")
    panel.get_by_role("button", name="Hinzufügen").click()
    panel = page.locator(".chat-members-panel")
    panel.locator("summary").click()
    assert panel.locator(".chat-member-list strong", has_text="Mira Browser").is_visible()
    assert panel.get_by_text("1 ausgewählt").is_visible()
    panel.get_by_role("button", name="Entfernen").click()
    panel = page.locator(".chat-members-panel")
    panel.locator("summary").click()
    assert panel.get_by_text("1 ausgewählt").is_visible()  # no silent audience widening
    panel.get_by_role("button", name="Mitgliederauswahl aufheben").click()
    assert page.locator(".chat-members-panel").get_by_text("Klassenraum").is_visible()

    composer = page.locator("[data-chat-composer]")
    composer.locator("textarea").fill(f"Prüfnachricht {width}")
    composer.get_by_role("button", name="Nachricht senden").click()
    message = page.locator(".message-row").filter(has_text=f"Prüfnachricht {width}")
    message.wait_for(state="visible")
    message.locator(".message-menu > summary").click()
    message.locator(".message-report > summary").click()
    message.get_by_role("button", name="Meldung senden").click()
    message = page.locator(".message-row").filter(has_text=f"Prüfnachricht {width}")
    message.locator(".message-menu > summary").click()
    message.get_by_role("button", name="Ausblenden").click()
    page.get_by_text("Diese Nachricht wurde von der Moderation ausgeblendet.").wait_for(state="visible")

    composer = page.locator("[data-chat-composer]")
    composer.locator("[data-chat-file]").set_input_files({
        "name": f"chat-test-{width}.pdf", "mimeType": "application/pdf",
        "buffer": b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\n%%EOF",
    })
    composer.get_by_role("button", name="Nachricht senden").click()
    attachment = page.locator(".chat-attachment").filter(has_text=f"chat-test-{width}.pdf")
    attachment.wait_for(state="visible")
    assert page.context.request.get(base + attachment.get_attribute("href")).status == 200
    composer = page.locator("[data-chat-composer]")
    composer.locator("[data-sticker-toggle]").click()
    sticker_button = composer.locator(f'[data-sticker-id="{fixture["sticker_id"]}"]')
    assert sticker_button.locator("img").evaluate("image => image.complete && image.naturalWidth > 0")
    sticker_button.click()
    assert composer.locator("[data-sticker-selection]").is_visible()
    composer.get_by_role("button", name="Nachricht senden").click()
    sticker_image = page.locator(".chat-message-sticker").last
    sticker_image.wait_for(state="visible")
    assert sticker_image.evaluate("image => image.complete && image.naturalWidth > 0")
    if width == 360:
        page.evaluate("""() => {
          Object.defineProperty(navigator, 'mediaDevices', {configurable: true, value: {
            getUserMedia: async () => ({getTracks: () => [{stop() {}}]})
          }});
          window.MediaRecorder = class {
            constructor() { this.state = 'inactive'; this.mimeType = 'audio/webm'; this.handlers = {}; }
            addEventListener(type, handler) { this.handlers[type] = handler; }
            start() { this.state = 'recording'; }
            stop() {
              this.state = 'inactive';
              this.handlers.dataavailable({data: new Blob(['synthetic audio'], {type: 'audio/webm'})});
              this.handlers.stop();
            }
          };
        }""")
        voice = composer.get_by_role("button", name="Sprachnachricht aufnehmen")
        voice.click()
        assert "Aufnahme läuft" in composer.locator("[data-composer-status]").inner_text()
        voice.click()
        assert "bereit zum Senden" in composer.locator("[data-composer-status]").inner_text()
        assert composer.locator("[data-chat-file]").evaluate("input => input.files.length === 1 && input.files[0].type === 'audio/webm'")
        composer.get_by_role("button", name="Nachricht senden").click()
        page.locator(".message-thread audio").last.wait_for(state="visible")
        composer = page.locator("[data-chat-composer]")
        page.evaluate("""() => {
          navigator.mediaDevices.getUserMedia = async () => {
            throw new DOMException('blocked', 'NotAllowedError');
          };
        }""")
        composer.get_by_role("button", name="Sprachnachricht aufnehmen").click()
        assert "Mikrofon ist blockiert" in composer.locator("[data-composer-status]").inner_text()
    page.screenshot(path=str(output / f"chat-full-clicks-{width}.png"), full_page=False)
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")

    page.goto(base + "/chat/")
    row = page.locator(".conversation-row-wrap").filter(has_text=title)
    row.locator(".conversation-menu > summary").click()
    row.get_by_role("button", name="Bearbeiten").click()
    edit = page.locator(".app-dialog[open]")
    edited_title = title + " bearbeitet"
    edit.locator('input[name="title"]').fill(edited_title)
    edit.get_by_role("button", name="Änderungen speichern").click()
    assert page.locator("#chat-room-heading").inner_text() == edited_title
    page.goto(base + "/chat/")
    row = page.locator(".conversation-row-wrap").filter(has_text=edited_title)
    row.locator(".conversation-menu > summary").click()
    row.get_by_role("button", name="Archivieren").click()
    page.goto(room_url)
    assert page.get_by_text("Dieser Raum ist archiviert. Nachrichten bleiben lesbar.").is_visible()
    assert page.locator("[data-chat-composer]").count() == 0
    page.goto(base + "/chat/")
    row = page.locator(".conversation-row-wrap").filter(has_text=edited_title)
    row.locator(".conversation-menu > summary").click()
    row.get_by_role("button", name="Löschen").click()
    page.locator(".conversation-row-wrap").filter(has_text=edited_title).wait_for(state="detached")
