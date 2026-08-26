from django.core.management.base import BaseCommand
from django.utils import timezone

from klasse5e.biometrics.client import VisionClient, VisionError
from klasse5e.biometrics.models import BiometricCollection


class Command(BaseCommand):
    help = "Löscht bei Testende/Abschaltung komplette Vision-Collections."

    def add_arguments(self, parser):
        parser.add_argument("--execute", action="store_true")

    def handle(self, *args, **options):
        collections = BiometricCollection.objects.exclude(status="disabled")
        self.stdout.write(f"due_collections={collections.count()}")
        if not options["execute"]:
            return
        client = VisionClient()
        for item in collections.iterator():
            item.status = "deletion_pending"
            item.disabled_at = timezone.now()
            item.save(update_fields=["status", "disabled_at"])
            try:
                client.delete_collection(str(item.vision_collection_id))
            except VisionError:
                self.stderr.write(str(item.public_id))
                continue
            item.biometricprofile_set.all().delete()
            item.visionphotosubmission_set.all().delete()
            item.status = "disabled"
            item.save(update_fields=["status"])
