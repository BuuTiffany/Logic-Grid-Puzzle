# api/management/commands/cleanup_puzzles.py
from django.core.management.base import BaseCommand
from django.conf import settings
from supabase import create_client

class Command(BaseCommand):
    help = "Delete used puzzles from Supabase to keep the pool clean."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show how many would be deleted without actually deleting.'
        )

    def handle(self, *args, **options):
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

        # Count first
        count_res = (
            client.table('puzzles')
            .select('id', count='exact')
            .eq('used', True)
            .execute()
        )
        count = count_res.count or 0

        if count == 0:
            self.stdout.write("No used puzzles to clean up.")
            return

        if options['dry_run']:
            self.stdout.write(f"Dry run: would delete {count} used puzzle(s).")
            return

        client.table('puzzles').delete().eq('used', True).execute()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} used puzzle(s)."))