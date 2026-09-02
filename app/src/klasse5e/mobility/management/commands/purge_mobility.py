from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from klasse5e.mobility.models import MobilityListing, PickupDisclosure


class Command(BaseCommand):
    help = "Expires mobility listings, erases stale pickup addresses and purges old records."

    @transaction.atomic
    def handle(self, *args, **options):
        now = timezone.now()
        today = timezone.localdate()
        expired = MobilityListing.objects.filter(
            status=MobilityListing.Status.ACTIVE, valid_until__lt=today
        ).update(status=MobilityListing.Status.EXPIRED)
        erased = (
            PickupDisclosure.objects.filter(revoked_at__isnull=True, valid_until__lte=now)
            .exclude(encrypted_address="")
            .update(encrypted_address="", revoked_at=now)
        )
        cutoff = now - timedelta(days=settings.MOBILITY_RETENTION_DAYS)
        purged, _ = MobilityListing.objects.filter(
            status__in=[MobilityListing.Status.EXPIRED, MobilityListing.Status.WITHDRAWN],
            updated_at__lt=cutoff,
        ).delete()
        self.stdout.write(f"expired={expired} addresses_erased={erased} records_purged={purged}")
