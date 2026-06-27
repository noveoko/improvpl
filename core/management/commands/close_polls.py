from django.core.management.base import BaseCommand

from core.services import close_expired_polls


class Command(BaseCommand):
    help = "Close expired polls and finalize polls that reached the vote threshold."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would happen without sending emails or updating polls.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run — no changes will be made."))

        expired_count, succeeded_count = close_expired_polls(send_email=not dry_run)

        self.stdout.write(
            self.style.SUCCESS(f"Done. Expired: {expired_count}, Succeeded: {succeeded_count}")
        )
