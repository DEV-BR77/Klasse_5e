import uuid
from io import BytesIO
from pathlib import Path

import qrcode
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A5
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from klasse5e.core.models import FamilyAccessCode, SchoolClass, UserAccount


class Command(BaseCommand):
    help = "Erzeugt einmalige Familiencodes und ein druckfertiges DIN-A5-Handout."

    def add_arguments(self, parser):
        parser.add_argument("--class-id", type=int, required=True)
        parser.add_argument("--count", type=int, default=40)
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        school_class = SchoolClass.objects.filter(pk=options["class_id"]).first()
        admin = UserAccount.objects.filter(is_superuser=True).order_by("id").first()
        if not school_class or not admin:
            raise CommandError("Klasse oder Hauptadministration fehlt.")
        count = max(1, min(100, options["count"]))
        batch_id = uuid.uuid4()
        invitations = []
        for serial in range(1, count + 1):
            item, token = FamilyAccessCode.issue(
                batch_id=batch_id,
                serial_number=serial,
                school_class=school_class,
                created_by=admin,
            )
            url = f"{settings.WAGTAILADMIN_BASE_URL.rstrip('/')}/familie/start/{token}/"
            invitations.append((item, url))
        output = Path(options["output"]).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        self._build_pdf(output, school_class, invitations)
        self.stdout.write(self.style.SUCCESS(f"{count} Einladungen erstellt: {output}"))
        self.stdout.write(f"Batch: {batch_id}")

    def _build_pdf(self, output, school_class, invitations):
        width, height = A5
        pdf = canvas.Canvas(str(output), pagesize=A5, pageCompression=1)
        pdf.setTitle(f"KlassID Familien-Einladungen {school_class.display_name}")
        for item, url in invitations:
            navy, teal, pale, coral = map(
                HexColor, ("#102D3B", "#35A4C6", "#EAF7FB", "#FF786C")
            )
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
            pdf.drawString(30, height - 144, "Alles Wichtige fuer Eltern und Kinder an einem Ort")

            qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_Q, box_size=8, border=4)
            qr.add_data(url)
            qr.make(fit=True)
            image = qr.make_image(fill_color="#102D3B", back_color="white")
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)
            qr_size = 172
            qr_x = (width - qr_size) / 2
            qr_y = height - 365
            pdf.setFillColor(white)
            pdf.roundRect(qr_x - 9, qr_y - 9, qr_size + 18, qr_size + 18, 16, fill=1, stroke=0)
            pdf.drawImage(ImageReader(buffer), qr_x, qr_y, qr_size, qr_size, mask="auto")
            pdf.setFillColor(navy)
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawCentredString(width / 2, qr_y - 27, "SCANNEN UND FAMILIE ANLEGEN")

            cards = (("K", "Kalender"), ("H", "Hausaufgaben"), ("M", "Mensa"), ("C", "Chat"), ("F", "Fotos"), ("W", "Schulweg"))
            start_x, card_y = 27, 118
            for index, (icon, label) in enumerate(cards):
                x = start_x + (index % 3) * 123
                y = card_y - (index // 3) * 51
                pdf.setFillColor(white)
                pdf.roundRect(x, y, 112, 40, 10, fill=1, stroke=0)
                pdf.setFillColor(teal if index % 2 == 0 else coral)
                pdf.circle(x + 20, y + 20, 12, fill=1, stroke=0)
                pdf.setFillColor(white)
                pdf.setFont("Helvetica-Bold", 9)
                pdf.drawCentredString(x + 20, y + 17, icon)
                pdf.setFillColor(navy)
                pdf.setFont("Helvetica-Bold", 8.5)
                pdf.drawString(x + 38, y + 17, label)

            pdf.setFillColor(navy)
            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawString(27, 27, f"Einladung {item.serial_number:02d} / {len(invitations):02d}")
            pdf.setFont("Helvetica", 6.5)
            pdf.drawRightString(width - 27, 28, "Einmalig gueltig - Familie einrichten - weitere Zugaenge persoenlich")
            pdf.setStrokeColor(teal)
            pdf.setLineWidth(1.2)
            pdf.line(27, 43, width - 27, 43)
            pdf.showPage()
        pdf.save()
