from django.core.management.base import BaseCommand
from django.utils import timezone

from chat.models import MessageAttachment


class Command(BaseCommand):
    help = "Delete expired Chat Lab attachment files and metadata."

    def handle(self, *args, **options):
        cutoff = timezone.now()
        deleted = 0

        while True:
            batch = list(
                MessageAttachment.objects.filter(expires_at__lte=cutoff)
                .order_by("pk")[:100]
            )
            if not batch:
                break
            for attachment in batch:
                if attachment.file.name:
                    attachment.file.storage.delete(attachment.file.name)
            _, counts = MessageAttachment.objects.filter(pk__in=[a.pk for a in batch]).delete()
            deleted += counts.get(MessageAttachment._meta.label, 0)

        self.stdout.write(self.style.SUCCESS(f"Purged {deleted} expired attachment(s)."))
