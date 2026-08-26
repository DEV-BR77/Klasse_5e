from django.core.management.base import BaseCommand

from klasse5e.biometrics.models import BiometricProfile
from klasse5e.biometrics.policies import biometric_consent
from klasse5e.biometrics.services import withdraw_profile


class Command(BaseCommand):
    help = "Sperrt und löscht Profile nach Widerruf oder fehlender Zustimmung."

    def handle(self, *args, **options):
        for profile in BiometricProfile.objects.filter(status__in=["active", "deletion_pending"]):
            allowed, _ = biometric_consent(profile.student.person)
            if allowed and profile.status == "active":
                continue
            try:
                withdraw_profile(profile)
            except Exception:
                self.stderr.write(str(profile.public_id))
