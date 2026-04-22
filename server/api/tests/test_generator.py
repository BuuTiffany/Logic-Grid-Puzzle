"""
Tests for the zebra puzzle generator.
Run with:  python test_generator.py
"""

from __future__ import annotations

import json
import time

from api.puzzles.generator import create_puzzle, solve_puzzle, category_values_from_solution, VALID_GRIDS, VALID_DIFFICULTIES
from api.puzzles.display import puzzle_to_dict, print_puzzle


# ── helpers ─────────────────────────────────────────────────────────────────

def verify_unique(puzzle) -> bool:
    cv = category_values_from_solution(puzzle.solution)
    solutions = solve_puzzle(puzzle.cols, puzzle.categories, cv, puzzle.clues)
    return len(solutions) == 1


def solution_matches(puzzle) -> bool:
    """Check that the CSP solution matches our stored solution."""
    cv = category_values_from_solution(puzzle.solution)
    solutions = solve_puzzle(puzzle.cols, puzzle.categories, cv, puzzle.clues)
    if not solutions:
        return False
    csp_sol = solutions[0]
    for cat in puzzle.categories:
        for val in puzzle.solution[cat]:
            expected_pos = puzzle.solution[cat].index(val) + 1  # 1-indexed
            if csp_sol.get(f"{cat}:{val}") != expected_pos:
                return False
    return True


# ── individual tests ─────────────────────────────────────────────────────────

def test_all_grids_and_difficulties():
    print("=== Test: All grid × difficulty combinations ===\n")
    results = []

    for grid in sorted(VALID_GRIDS):
        for diff in VALID_DIFFICULTIES:
            label = f"{grid} / {diff}"
            t0 = time.time()
            try:
                puzzle = create_puzzle(grid=grid, difficulty=diff, seed=42)
                elapsed = time.time() - t0
                unique = verify_unique(puzzle)
                matches = solution_matches(puzzle)
                status = "✓ PASS" if (unique and matches) else "✗ FAIL"
                note = f"{len(puzzle.clues)} clues, {elapsed:.2f}s"
                if not unique:
                    note += " [NOT UNIQUE]"
                if not matches:
                    note += " [SOLUTION MISMATCH]"
            except Exception as e:
                elapsed = time.time() - t0
                status = "✗ ERROR"
                note = str(e)
            row = f"  {status}  {label:<18s}  {note}"
            print(row)
            results.append(status.startswith("✓"))

    total = len(results)
    passed = sum(results)
    print(f"\n  {passed}/{total} passed\n")
    return passed == total


def test_reproducibility():
    print("=== Test: Reproducibility with same seed ===\n")
    p1 = create_puzzle(grid="4x5", difficulty="moderate", seed=7)
    p2 = create_puzzle(grid="4x5", difficulty="moderate", seed=7)
    same_solution = p1.solution == p2.solution
    same_clues = [c.clue_type for c in p1.clues] == [c.clue_type for c in p2.clues]
    ok = same_solution and same_clues
    print(f"  {'✓ PASS' if ok else '✗ FAIL'}  Same seed → same puzzle: solution={same_solution}, clues={same_clues}\n")
    return ok


def test_different_seeds():
    print("=== Test: Different seeds → different puzzles ===\n")
    p1 = create_puzzle(grid="4x5", difficulty="moderate", seed=1)
    p2 = create_puzzle(grid="4x5", difficulty="moderate", seed=2)
    different = p1.solution != p2.solution
    print(f"  {'✓ PASS' if different else '✗ FAIL'}  Different seeds → different solutions: {different}\n")
    return different


def test_clue_counts_by_difficulty():
    print("=== Test: Easy has more clues than challenging ===\n")
    easy = create_puzzle(grid="4x5", difficulty="easy", seed=99)
    mod  = create_puzzle(grid="4x5", difficulty="moderate", seed=99)
    hard = create_puzzle(grid="4x5", difficulty="challenging", seed=99)
    print(f"  easy={len(easy.clues)} clues, moderate={len(mod.clues)} clues, challenging={len(hard.clues)} clues")
    ok = len(easy.clues) >= len(mod.clues) >= len(hard.clues)
    print(f"  {'✓ PASS' if ok else '✗ FAIL'}  Ordering: easy ≥ moderate ≥ challenging\n")
    return ok


def test_json_serialization():
    print("=== Test: JSON serialization round-trip ===\n")
    puzzle = create_puzzle(grid="3x4", difficulty="easy", seed=5)
    d = puzzle_to_dict(puzzle)
    json_str = json.dumps(d)
    restored = json.loads(json_str)
    ok = restored["grid"] == "3x4" and len(restored["clues"]) > 0
    print(f"  {'✓ PASS' if ok else '✗ FAIL'}  JSON serialization ok, {len(restored['clues'])} clues\n")
    return ok


def test_invalid_inputs():
    print("=== Test: Invalid inputs raise errors ===\n")
    errors = []
    for bad_grid, bad_diff in [("5x5", "moderate"), ("4x5", "hard"), ("2x3", "easy")]:
        try:
            create_puzzle(grid=bad_grid, difficulty=bad_diff)
            errors.append(f"  ✗ FAIL  Expected error for grid={bad_grid!r} diff={bad_diff!r}")
        except ValueError:
            errors.append(f"  ✓ PASS  Raised ValueError for grid={bad_grid!r} diff={bad_diff!r}")
    for e in errors:
        print(e)
    ok = all("PASS" in e for e in errors)
    print()
    return ok


def demo_print():
    print("=== Demo: Sample 4x5 moderate puzzle (with solution) ===\n")
    puzzle = create_puzzle(grid="4x5", difficulty="moderate", seed=123)
    print_puzzle(puzzle, reveal_solution=True)


# ── runner ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    all_pass = all([
        test_all_grids_and_difficulties(),
        test_reproducibility(),
        test_different_seeds(),
        test_clue_counts_by_difficulty(),
        test_json_serialization(),
        test_invalid_inputs(),
    ])
    demo_print()
    print("=" * 60)
    print(f"  Overall: {'ALL TESTS PASSED ✓' if all_pass else 'SOME TESTS FAILED ✗'}")
    print("=" * 60)
