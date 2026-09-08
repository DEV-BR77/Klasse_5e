from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from klasse5e.webuntis.absences import absence_data_allowed, child_contexts
from klasse5e.webuntis.models import AbsenceDraft, WebUntisAbsence


class Command(BaseCommand):
    help = "Deletes expired absence data and records without current access/consent."

    def handle(self, *args, **options):
        cutoff = timezone.localdate() - timedelta(days=90)
        WebUntisAbsence.objects.filter(ends_on__lt=cutoff).delete()
        AbsenceDraft.objects.filter(created_at__lt=timezone.now() - timedelta(days=30)).delete()
        for draft in AbsenceDraft.objects.select_related("user"):
            if draft.student_id not in {c.student.pk for c in child_contexts(draft.user)}:
                draft.delete()
        for item in WebUntisAbsence.objects.select_related("connection__user"):
            if not absence_data_allowed(item.connection.student):
                item.delete()
