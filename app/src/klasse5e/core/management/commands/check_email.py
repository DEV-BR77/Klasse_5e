from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import get_connection, send_mail
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email


class Command(BaseCommand):
    help = "Prüft SMTP mit TLS und Anmeldung; sendet nur mit --recipient eine Testmail."

    def add_arguments(self, parser):
        parser.add_argument("--recipient")

    def handle(self, *args, **options):
        if settings.EMAIL_BACKEND != "django.core.mail.backends.smtp.EmailBackend":
            raise CommandError("Kein SMTP-Versand aktiv; Test würde keine Zustellung prüfen.")
        if not settings.EMAIL_HOST_PASSWORD:
            raise CommandError("Versandsschlüssel fehlt: secret://providers/resend/klassid_api_key")
        recipient = options["recipient"]
        if recipient:
            try:
                validate_email(recipient)
            except ValidationError:
                raise CommandError("Ungültige Empfängeradresse.") from None
        try:
            with get_connection(fail_silently=False) as connection:
                if recipient:
                    count = send_mail(
                        "KlassID – E-Mail-Versandtest",
                        "Dies ist die angeforderte Testmail für den KlassID-Versand. Sie enthält keine Anmeldedaten und erfordert keine Aktion.",
                        settings.DEFAULT_FROM_EMAIL,
                        [recipient],
                        connection=connection,
                    )
                    if count != 1:
                        raise CommandError("Die Testmail wurde nicht angenommen.")
        except Exception as exc:
            raise CommandError(
                f"SMTP-Prüfung fehlgeschlagen ({type(exc).__name__}); keine Zugangsdaten ausgegeben."
            ) from None
        self.stdout.write(
            self.style.SUCCESS(
                "Testmail vom Versanddienst angenommen; Posteingang/Zustellstatus prüfen."
                if recipient
                else "SMTP-Verbindung, TLS und Anmeldung erfolgreich."
            )
        )
