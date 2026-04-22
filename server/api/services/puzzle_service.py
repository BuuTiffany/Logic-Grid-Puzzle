"""
Service layer for puzzle generation, storage, and retrieval.
All Supabase interaction lives here — views and commands stay thin.
"""

from __future__ import annotations

import random
import logging
from typing import Optional

from django.conf import settings
from supabase import create_client, Client

from api.puzzles.generator import create_puzzle

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Supabase client (module-level singleton)
# ---------------------------------------------------------------------------

_supabase: Optional[Client] = None


def _client() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    return _supabase


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------

def _to_public(row: dict) -> dict:
    """Strip solution from a Supabase row before returning to a view."""
    public = dict(row)
    public.pop("solution", None)
    return public


def _puzzle_to_storage_dict(puzzle, seed: int) -> dict:
    """Full record for inserting into Supabase. Columns must match the table schema exactly."""
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


def _puzzle_to_public_dict(puzzle, stored_id: str) -> dict:
    """Public shape returned to views — no solution, includes Supabase id."""
    return {
        "id":         stored_id,
        "grid":       f"{puzzle.rows}x{puzzle.cols}",
        "difficulty": puzzle.difficulty,
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
    }


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------

def generate_and_store(grid: str = "4x5", difficulty: str = "moderate", seed: int = None) -> dict:
    """
    Generate a puzzle, persist it to Supabase, and return the public shape
    (no solution) with the assigned Supabase UUID included.
    """
    if seed is None:
        seed = random.randint(0, 2 ** 31)

    puzzle = create_puzzle(grid=grid, difficulty=difficulty, seed=seed)
    record = _puzzle_to_storage_dict(puzzle, seed)

    res = _client().table("puzzles").insert(record).execute()

    if not res.data:
        raise RuntimeError(f"Supabase insert returned no data. Response: {res}")

    stored_id = res.data[0]["id"]
    logger.info("Stored puzzle id=%s grid=%s difficulty=%s seed=%s", stored_id, grid, difficulty, seed)

    return _puzzle_to_public_dict(puzzle, stored_id)


def fetch_puzzle_private(puzzle_id: str) -> dict | None:
    """
    Fetch a full puzzle record including solution.
    For server-side validation only — never forward this to the client.
    Returns None if the puzzle does not exist.
    """
    res = (
        _client()
        .table("puzzles")
        .select("*")
        .eq("id", puzzle_id)
        .maybe_single()
        .execute()
    )
    return res.data


def get_or_generate(grid: str = "4x5", difficulty: str = "moderate") -> dict:
    """
    Serve a pre-seeded puzzle from the pool without generating on the fly.
    Falls back to live generation if the pool is empty.
    Marks the served puzzle as used so it isn't served twice.
    Returns the public puzzle dict (no solution) with 'id'.
    """
    res = (
        _client()
        .table("puzzles")
        .select("*")
        .eq("grid", grid)
        .eq("difficulty", difficulty)
        .eq("used", False)
        .order("created_at")
        .limit(1)
        .execute()
    )

    if res.data:
        row = res.data[0]
        _client().table("puzzles").update({"used": True}).eq("id", row["id"]).execute()
        logger.info("Served pre-seeded puzzle id=%s", row["id"])
        return _to_public(row)

    logger.warning("Puzzle pool empty for grid=%s difficulty=%s — generating live", grid, difficulty)
    return generate_and_store(grid=grid, difficulty=difficulty)


def validate_solution(puzzle_id: str, user_solution: dict) -> bool:
    """
    Returns True if correct, False if wrong, raises ValueError if puzzle not found.
    """
    record = fetch_puzzle_private(puzzle_id)
    if record is None:
        raise ValueError(f"Puzzle {puzzle_id!r} not found.")
    return record["solution"] == user_solution


def get_hint(puzzle_id: str, category: str, position: int) -> str | None:
    """
    Return the correct value for a given category and 0-indexed position.
    Returns None if the puzzle is not found or inputs are out of range.
    """
    record = fetch_puzzle_private(puzzle_id)
    if record is None:
        return None

    solution: dict = record["solution"]
    values: list = solution.get(category, [])

    if position < 0 or position >= len(values):
        return None

    return values[position]