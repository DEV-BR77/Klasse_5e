from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.core.signing import TimestampSigner


class Command(BaseCommand):
    help = "Erzeugt einen 20 Minuten gültigen Scan-Link für einen bestehenden Benutzer."

    def add_arguments(self, parser):
        parser.add_argument("email")

    def handle(self, *args, **options):
        user = get_user_model().objects.filter(email__iexact=options["email"], is_active=True).first()
        if user is None:
            raise CommandError("Aktiver Benutzer nicht gefunden.")
        token = TimestampSigner(salt="klassid-scan-access").sign(str(user.pk))
        base = getattr(settings, "PUBLIC_BASE_URL", "https://5e.klassid.de").rstrip("/")
        self.stdout.write(f"{base}/scan/{token}/")
