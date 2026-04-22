"""
Puzzle display and serialization utilities.
"""

from __future__ import annotations

import json
from typing import Any

from api.puzzles.generator import Puzzle

# ---------------------------------------------------------------------------
# Pretty-print
# ---------------------------------------------------------------------------

def print_puzzle(puzzle: Puzzle, reveal_solution: bool = False) -> None:
    cols = puzzle.cols
    cats = puzzle.categories

    header = f"  Zebra Puzzle  |  {puzzle.rows} categories × {puzzle.cols} houses  |  {puzzle.difficulty.capitalize()}"
    print("=" * len(header))
    print(header)
    print("=" * len(header))
    print()

    print(f"There are {cols} houses in a row, numbered 1 to {cols} from left to right.")
    print(f"Each house has exactly one value for each of these {puzzle.rows} attributes:")
    for cat in cats:
        vals = ", ".join(puzzle.solution[cat])
        print(f"  • {cat.capitalize()}: {vals}")
    print()

    print("─" * 60)
    print("CLUES")
    print("─" * 60)
    for i, clue in enumerate(puzzle.clues, 1):
        print(f"  {i:2d}. {clue.to_text(cols)}")
    print()

    if reveal_solution:
        _print_solution_table(puzzle)


def _print_solution_table(puzzle: Puzzle) -> None:
    cols = puzzle.cols
    cats = puzzle.categories
    col_w = 14

    print("─" * 60)
    print("SOLUTION")
    print("─" * 60)
    header = f"{'':12s}" + "".join(f"House {i:<{col_w - 7}}" for i in range(1, cols + 1))
    print(header)
    print("  " + "─" * (12 + col_w * cols))
    for cat in cats:
        row = f"  {cat.capitalize():<10s}" + "".join(
            f"{v:<{col_w}}" for v in puzzle.solution[cat]
        )
        print(row)
    print()


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

def _puzzle_to_storage_dict(puzzle, seed: int) -> dict:
    return {
        "grid":       f"{puzzle.rows}x{puzzle.cols}",
        "difficulty": puzzle.difficulty,
        "seed":       seed,
        "categories": puzzle.categories,
        "clues": [
            {
                "id":       i + 1,
                "type":     c.clue_type,
                "text":     c.to_text(puzzle.cols),
                "cat1":     c.cat1,
                "val1":     c.val1,
                "cat2":     c.cat2,
                "val2":     c.val2,
                "position": c.position,
            }
            for i, c in enumerate(puzzle.clues)
        ],
        "solution":   puzzle.solution,
        "used":       False,
    }


def puzzle_to_json(puzzle: Puzzle, indent: int = 2) -> str:
    return json.dumps(puzzle_to_dict(puzzle), indent=indent)
