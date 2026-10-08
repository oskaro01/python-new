"""Process queued shop jobs once, suitable for a scheduler or worker loop."""

from django.core.management.base import BaseCommand

from shop.jobs import process_jobs


class Command(BaseCommand):
    help = "Process available background jobs for the checkout lab."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=1,
            help="Maximum number of jobs to process (default: 1).",
        )

    def handle(self, *args, **options):
        limit = max(options["limit"], 1)
        jobs = process_jobs(limit=limit)
        if not jobs:
            self.stdout.write("No available jobs.")
            return
        for job in jobs:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Job #{job.pk}: {job.get_status_display()} "
                    f"after {job.attempts} attempt(s)"
                )
            )
