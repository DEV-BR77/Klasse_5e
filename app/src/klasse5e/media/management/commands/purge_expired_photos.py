from django.core.management.base import BaseCommand
from django.utils import timezone

from klasse5e.core.models import AuditEvent
from klasse5e.media.models import Photo
from klasse5e.media.services import delete_photo_files


class Command(BaseCommand):
    help = "Listet oder löscht abgelaufene Galeriefotos anhand opaque IDs."

    def add_arguments(self, parser):
        parser.add_argument("--delete", action="store_true")

    def handle(self, *args, **options):
        photos = Photo.objects.filter(retention_until__lte=timezone.now()).exclude(status="deleted")
        for photo in photos.iterator():
            self.stdout.write(str(photo.id))
            if options["delete"]:
                delete_photo_files(photo)
                AuditEvent.objects.create(
                    actor=None,
                    action="photo.retention_deleted",
                    target_type="photo",
                    target_id=str(photo.id),
                )
        self.stdout.write(
            f"count={photos.count()} mode={'delete' if options['delete'] else 'dry-run'}"
        )
