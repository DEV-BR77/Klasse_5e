from django.core.management.base import BaseCommand
from django.utils import timezone

from klasse5e.biometrics.client import VisionClient, VisionError
from klasse5e.biometrics.models import BiometricMatch, VisionPhotoSubmission


class Command(BaseCommand):
    help = "Entfernt fällige Vision-Quelldateien und abgelaufene technische Zuordnungen."

    def add_arguments(self, parser):
        parser.add_argument("--execute", action="store_true")

    def handle(self, *args, **options):
        now = timezone.now()
        due = VisionPhotoSubmission.objects.filter(
            source_delete_due_at__lte=now, source_deleted_at__isnull=True
        ).exclude(status="deleted")
        self.stdout.write(f"due_sources={due.count()}")
        if not options["execute"]:
            return
        client = VisionClient()
        for item in due.iterator():
            try:
                client.purge_image_source(
                    str(item.collection.vision_collection_id), str(item.vision_image_id)
                )
            except VisionError:
                item.error_code = "source_purge_failed"
                item.save(update_fields=["error_code"])
                continue
            item.source_deleted_at = now
            item.status = "source_purged"
            item.save(update_fields=["source_deleted_at", "status"])
            self.stdout.write(str(item.public_id))
        cutoff = now - timezone.timedelta(days=30)
        BiometricMatch.objects.filter(
            created_at__lt=cutoff, status__in=["rejected", "deleted"]
        ).delete()
