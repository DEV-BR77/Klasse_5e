import uuid
from io import BytesIO
from pathlib import Path

import qrcode
from django.conf import settings
from django.db import transaction
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A5
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .models import FamilyAccessCode


@transaction.atomic
def create_family_handout(*, school_class, count, created_by, family_names=None, max_uses=1):
    count = max(1, min(100, int(count)))
    max_uses = max(1, min(100, int(max_uses)))
    names = [name.strip()[:120] for name in (family_names or []) if name.strip()]
    batch_id = uuid.uuid4()
    invitations = []
    for serial in range(1, count + 1):
        intended_name = names[serial - 1] if serial <= len(names) else ""
        item, token = FamilyAccessCode.issue(
            batch_id=batch_id,
            serial_number=serial,
            school_class=school_class,
            created_by=created_by,
            max_uses=max_uses,
        )
        if intended_name:
            item.intended_family_name = intended_name
            item.save(update_fields=["intended_family_name"])
        url = f"{settings.WAGTAILADMIN_BASE_URL.rstrip('/')}/familie/start/{token}/"
        invitations.append((item, url, token))
    output = BytesIO()
    _build_pdf(output, school_class, invitations)
    output.seek(0)
    return output, batch_id


def _build_pdf(output, school_class, invitations):
    width, height = A5
    pdf = canvas.Canvas(output, pagesize=A5, pageCompression=1)
    pdf.setTitle(f"KlassID Familien-Einladungen {school_class.display_name}")
    for item, url, token in invitations:
        navy, teal, pale = map(HexColor, ("#102D3B", "#35A4C6", "#EAF7FB"))
        pdf.setFillColor(pale)
        pdf.rect(0, 0, width, height, fill=1, stroke=0)
        pdf.setFillColor(navy)
        pdf.roundRect(0, height - 175, width, 210, 34, fill=1, stroke=0)
        pdf.setFillColor(teal)
        pdf.circle(width - 25, height - 42, 62, fill=1, stroke=0)
        pdf.setFillColor(white)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(28, height - 42, "KlassID")
        pdf.setFont("Helvetica-Bold", 27)
        pdf.drawString(28, height - 88, "Kommt in unseren")
        pdf.drawString(28, height - 119, "Klassentreff")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(30, height - 144, "Alles Wichtige fuer Eltern und Schueler an einem Ort")

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=8,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        image = qr.make_image(fill_color="#102D3B", back_color="white")
        image_buffer = BytesIO()
        image.save(image_buffer, format="PNG")
        image_buffer.seek(0)
        qr_size = 172
        qr_x = (width - qr_size) / 2
        qr_y = height - 365
        pdf.setFillColor(white)
        pdf.roundRect(qr_x - 9, qr_y - 9, qr_size + 18, qr_size + 18, 16, fill=1, stroke=0)
        pdf.drawImage(ImageReader(image_buffer), qr_x, qr_y, qr_size, qr_size, mask="auto")
        pdf.setFillColor(navy)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawCentredString(width / 2, qr_y - 27, "SCANNEN UND FAMILIE ANLEGEN")
        pdf.setFont("Helvetica-Bold", 8.5)
        pdf.drawCentredString(width / 2, qr_y - 43, "Einladungscode")
        pdf.setFont("Courier-Bold", 11)
        pdf.drawCentredString(width / 2, qr_y - 58, token)

        icon_dir = Path(settings.BASE_DIR) / "static" / "branding" / "icons" / "processed"
        icon_layout = (
            ("01-fahrradroute.png", 24, 382, 55, 55, -8),
            ("02-kalender.png", 342, 382, 50, 50, 7),
            ("03-mensa.png", 20, 300, 52, 52, -5),
            ("04-buch-hausaufgaben.png", 350, 300, 52, 52, 6),
            ("05-chat.png", 22, 205, 52, 52, -7),
            ("06-fotogalerie.png", 350, 205, 52, 52, 8),
            ("07-checkliste.png", 24, 104, 52, 52, -5),
            ("08-ical.png", 342, 104, 52, 52, 6),
            ("09-push-benachrichtigung.png", 108, 70, 48, 48, -7),
            ("11-kinder-datenschutz.png", 264, 70, 52, 52, 7),
        )
        for filename, x, y, icon_width, icon_height, _angle in icon_layout:
            icon_path = icon_dir / filename
            if icon_path.is_file():
                pdf.drawImage(
                    ImageReader(str(icon_path)),
                    x,
                    y,
                    icon_width,
                    icon_height,
                    mask="auto",
                )
        pdf.setFillColor(navy)
        if item.intended_family_name:
            pdf.setFont("Helvetica-Bold", 7.5)
            pdf.drawCentredString(width / 2, 51, f"Vorgesehen fuer: {item.intended_family_name}")
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(27, 27, f"Einladung {item.serial_number:02d} / {len(invitations):02d}")
        pdf.setFont("Helvetica", 6.5)
        validity_label = (
            "Einmalig gueltig"
            if item.max_uses == 1
            else f"Mehrfach gueltig - bis zu {item.max_uses} Familien"
        )
        pdf.drawRightString(width - 27, 28, f"{validity_label} - persoenliche Zugaenge")
        pdf.setStrokeColor(teal)
        pdf.setLineWidth(1.2)
        pdf.line(27, 43, width - 27, 43)
        pdf.showPage()
    pdf.save()
