import time

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import close_old_connections


class Command(BaseCommand):
    help = "Run periodic message and attachment cleanup outside web requests."

    def add_arguments(self, parser):
        parser.add_argument("--interval", type=int, default=30, help="Seconds between cleanup runs.")
        parser.add_argument("--once", action="store_true", help="Run one cleanup pass and exit.")

    def handle(self, *args, **options):
        if options["interval"] <= 0:
            raise CommandError("--interval must be greater than zero.")
        self.stdout.write("Chat cleanup started. Stop with Ctrl+C.")
        try:
            while True:
                close_old_connections()
                # One process schedules and executes two recurring jobs.
                # A Redis-backed queue can be introduced when multiple workers are needed.
                call_command("purge_expired_messages", stdout=self.stdout, stderr=self.stderr)
                call_command("purge_expired_attachments", stdout=self.stdout, stderr=self.stderr)
                close_old_connections()
                if options["once"]:
                    break
                time.sleep(options["interval"])
        except KeyboardInterrupt:
            self.stdout.write("Chat cleanup stopped.")
        finally:
            close_old_connections()
