from __future__ import annotations

import random
import logging
from typing import Optional

from django.conf import settings
from supabase import create_client, Client

from api.puzzles.generator import create_puzzle
from api.puzzles.display import puzzle_to_dict

logger = logging.getLogger(__name__)

_supabase: Optional[Client] = None


def _client() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    return _supabase

def _to_public(row: dict) -> dict:
    """Strip solution from a Supabase row before returning to a view."""
    public = dict(row)
    public.pop("solution", None)
    return public

def _puzzle_to_storage_dict(puzzle, seed: int) -> dict:
    """Full record for inserting into Supabase. Includes solution."""
    data = puzzle_to_dict(puzzle)
    data["seed"] = seed
    data["used"] = False
    return data

def generate_and_store(grid: str = "4x5", difficulty: str = "moderate", seed: int = None) -> dict:
    """Returns a dict: public puzzle dict with 'id' key added"""
    if seed is None:
        seed = random.randint(0, 2 ** 31)

    puzzle = create_puzzle(grid=grid, difficulty=difficulty, seed=seed)
    record = _puzzle_to_storage_dict(puzzle, seed)

    res = _client().table("puzzles").insert(record).execute()

    if not res.data:
        raise RuntimeError(f"Supabase insert returned no data. Response: {res}")

    stored_id = res.data[0]["id"]
    logger.info("Stored puzzle id=%s grid=%s difficulty=%s seed=%s", stored_id, grid, difficulty, seed)

    public = _to_public(puzzle_to_dict(puzzle))
    public["id"] = stored_id
    return public


def fetch_puzzle_private(puzzle_id: str) -> dict | None:
    """
    Fetch a full puzzle record including solution.
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
    return res.data  # None if not found


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
    Compare user_solution against the stored solution server-side.
    Returns True if correct, False if wrong, raises ValueError if puzzle not found.
    """
    record = fetch_puzzle_private(puzzle_id)
    if record is None:
        raise ValueError(f"Puzzle {puzzle_id!r} not found.")
    return record["solution"] == user_solution


def get_hint(puzzle_id: str, category: str, position: int) -> str | None:
    """
    Return the correct value for a given category and 0-indexed position.
    Used by the hint endpoint to reveal a single cell.
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