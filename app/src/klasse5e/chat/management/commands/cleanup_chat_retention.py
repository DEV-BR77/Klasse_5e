from django.core.management.base import BaseCommand

from klasse5e.chat.retention import cleanup_expired_messages


class Command(BaseCommand):
    help = "Deletes chat messages and attachments after their configured retention period."

    def handle(self, *args, **options):
        self.stdout.write(str(cleanup_expired_messages()))
