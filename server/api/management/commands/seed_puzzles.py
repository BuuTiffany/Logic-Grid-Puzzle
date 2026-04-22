"""
Management command to pre-generate puzzles and store them in Supabase.

Usage:
    python manage.py seed_puzzles                          # 10 of every grid/difficulty
    python manage.py seed_puzzles --count 20               # 20 of every grid/difficulty
    python manage.py seed_puzzles --grid 4x5               # all difficulties for 4x5
    python manage.py seed_puzzles --grid 4x5 --difficulty challenging --count 5
"""

from django.core.management.base import BaseCommand

from api.puzzles.generator import VALID_GRIDS, VALID_DIFFICULTIES
from api.services.puzzle_service import generate_and_store


class Command(BaseCommand):
    help = "Pre-generate zebra puzzles and seed them into Supabase."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Number of puzzles to generate per grid/difficulty combination (default: 10)",
        )
        parser.add_argument(
            "--grid",
            type=str,
            default=None,
            help=f"Specific grid to seed. One of {VALID_GRIDS}. Omit for all grids.",
        )
        parser.add_argument(
            "--difficulty",
            type=str,
            default=None,
            help=f"Specific difficulty to seed. One of {VALID_DIFFICULTIES}. Omit for all.",
        )

    def handle(self, *args, **options):
        count = options["count"]
        grids = [options["grid"]] if options["grid"] else sorted(VALID_GRIDS)
        difficulties = [options["difficulty"]] if options["difficulty"] else list(VALID_DIFFICULTIES)

        # Validate args early
        for g in grids:
            if g not in VALID_GRIDS:
                self.stderr.write(self.style.ERROR(f"Invalid grid: {g!r}. Must be one of {VALID_GRIDS}"))
                return
        for d in difficulties:
            if d not in VALID_DIFFICULTIES:
                self.stderr.write(self.style.ERROR(f"Invalid difficulty: {d!r}. Must be one of {VALID_DIFFICULTIES}"))
                return

        total = len(grids) * len(difficulties) * count
        self.stdout.write(f"Seeding {total} puzzles ({len(grids)} grids × {len(difficulties)} difficulties × {count} each)...\n")

        success = 0
        failed = 0

        for grid in grids:
            for diff in difficulties:
                self.stdout.write(f"  {grid} / {diff}")
                for i in range(count):
                    try:
                        result = generate_and_store(grid=grid, difficulty=diff)
                        self.stdout.write(f"    [{i + 1}/{count}] id={result['id']}")
                        success += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"    [{i + 1}/{count}] FAILED: {e}"))
                        failed += 1

        self.stdout.write("")
        if failed == 0:
            self.stdout.write(self.style.SUCCESS(f"Done. {success}/{total} puzzles seeded successfully."))
        else:
            self.stdout.write(self.style.WARNING(f"Done. {success} succeeded, {failed} failed."))