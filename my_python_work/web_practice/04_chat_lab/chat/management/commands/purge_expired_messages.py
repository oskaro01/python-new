from django.core.management.base import BaseCommand
from django.utils import timezone

from chat.models import Message


class Command(BaseCommand):
    help = "Delete expired messages and their private attachment files."

    def handle(self, *args, **options):
        cutoff = timezone.now()
        deleted = 0

        while True:
            # Small batches bound memory use and avoid a cursor held over deletes.
            batch = list(
                Message.objects.filter(expires_at__lte=cutoff)
                .order_by("pk").prefetch_related("attachments")[:100]
            )
            if not batch:
                break

            for message in batch:
                for attachment in message.attachments.all():
                    if attachment.file.name:
                        attachment.file.storage.delete(attachment.file.name)

            # File deletion comes first; a failure leaves rows available for retry.
            # Missing local files are harmless when the same job runs again.
            _, counts = Message.objects.filter(pk__in=[m.pk for m in batch]).delete()
            deleted += counts.get(Message._meta.label, 0)

        self.stdout.write(self.style.SUCCESS(f"Purged {deleted} expired message(s)."))
