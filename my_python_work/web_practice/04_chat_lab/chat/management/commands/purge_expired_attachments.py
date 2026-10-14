from django.core.management.base import BaseCommand
from django.utils import timezone

from chat.models import MessageAttachment


class Command(BaseCommand):
    help = "Delete expired Chat Lab attachment files and metadata."

    def handle(self, *args, **options):
        expired = MessageAttachment.objects.filter(expires_at__lte=timezone.now())
        deleted = 0

        for attachment in expired.iterator():
            if attachment.file.name:
                attachment.file.storage.delete(attachment.file.name)
            attachment.delete()
            deleted += 1

        self.stdout.write(self.style.SUCCESS(f"Purged {deleted} expired attachment(s)."))
