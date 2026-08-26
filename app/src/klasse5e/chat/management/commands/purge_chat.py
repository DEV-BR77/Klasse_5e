from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from klasse5e.chat.models import ChatMessage


class Command(BaseCommand):
    help = "Löscht abgelaufene Chatnachrichten; standardmäßig nur Dry-Run."

    def add_arguments(self, parser):
        parser.add_argument("--execute", action="store_true")

    def handle(self, *args, **options):
        cutoff = timezone.now() - timezone.timedelta(days=settings.CHAT_RETENTION_DAYS)
        query = ChatMessage.objects.filter(created_at__lt=cutoff)
        self.stdout.write(f"expired_messages={query.count()}")
        if options["execute"]:
            query.delete()
