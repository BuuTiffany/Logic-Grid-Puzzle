"""
Zebra / Einstein Puzzle Generator
==================================
Generates logic puzzles with a unique solution for grid sizes:
  3x4, 3x5, 4x4, 4x5, 4x6, 4x7
and difficulty levels: easy, moderate, challenging.

Grid notation: <rows>x<cols>
  rows = number of attribute categories  (e.g. 4 → color, nationality, drink, pet)
  cols = number of houses / positions    (e.g. 5 → houses 1-5)

No external dependencies — uses the bundled csp.py solver.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional

from api.puzzles.csp import CSP

# ---------------------------------------------------------------------------
# Attribute pool
# ---------------------------------------------------------------------------

ATTRIBUTE_POOL: dict[str, list[str]] = {
    "color":       ["Red", "Blue", "Green", "Yellow", "White", "Orange", "Purple", "Pink"],
    "nationality": ["English", "Spanish", "Ukrainian", "Norwegian", "Japanese",
                    "German", "French", "Italian"],
    "drink":       ["Coffee", "Tea", "Milk", "Water", "OrangeJuice",
                    "Beer", "Wine", "Lemonade"],
    "pet":         ["Dog", "Snail", "Fox", "Horse", "Zebra",
                    "Cat", "Bird", "Fish"],
    "smoke":       ["OldGold", "Kools", "Chesterfield", "LuckyStrike", "Parliament",
                    "Marlboro", "Camel", "Winston"],
    "sport":       ["Football", "Tennis", "Swimming", "Chess", "Hockey",
                    "Baseball", "Golf", "Cycling"],
    "job":         ["Doctor", "Lawyer", "Engineer", "Artist", "Teacher",
                    "Chef", "Pilot", "Nurse"],
    "music":       ["Jazz", "Rock", "Classical", "Pop", "Blues",
                    "Country", "Metal", "Reggae"],
}

# Fixed category order (first N are used for a puzzle)
CATEGORY_ORDER = ["color", "nationality", "drink", "pet", "smoke", "sport", "job", "music"]

VALID_GRIDS = {"3x4", "3x5", "4x4", "4x5", "4x6", "4x7"}
VALID_DIFFICULTIES = {"easy", "moderate", "challenging"}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Clue:
    clue_type: str          # "same_house" | "left_of" | "next_to" | "position" | "not_same"
    cat1: str
    val1: str
    cat2: Optional[str] = None
    val2: Optional[str] = None
    position: Optional[int] = None   # 1-indexed, used for "position" clues

    def to_text(self, cols: int) -> str:
        """Return a human-readable clue string."""
        ordinals = {1: "first", 2: "second", 3: "third", 4: "fourth",
                    5: "fifth", 6: "sixth", 7: "seventh"}
        if self.clue_type == "same_house":
            return f"The person with {self.val1} also has {self.val2}."
        if self.clue_type == "left_of":
            return (f"The {self.val1} house is immediately to the left "
                    f"of the {self.val2} house.")
        if self.clue_type == "next_to":
            return (f"The person with {self.val1} lives next to "
                    f"the person with {self.val2}.")
        if self.clue_type == "position":
            mid = (cols + 1) // 2
            if self.position == mid and cols % 2 == 1:
                return f"The person with {self.val1} lives in the middle house."
            pos_word = ordinals.get(self.position, f"position {self.position}")
            return f"The person with {self.val1} lives in the {pos_word} house."
        if self.clue_type == "not_same":
            return f"The person with {self.val1} does not have {self.val2}."
        return "Unknown clue."

    def __hash__(self):
        return hash((self.clue_type, self.cat1, self.val1,
                     self.cat2, self.val2, self.position))

    def __eq__(self, other):
        if not isinstance(other, Clue):
            return False
        return (self.clue_type == other.clue_type and
                self.cat1 == other.cat1 and self.val1 == other.val1 and
                self.cat2 == other.cat2 and self.val2 == other.val2 and
                self.position == other.position)


@dataclass
class Puzzle:
    cols: int
    rows: int
    categories: list[str]
    solution: dict[str, list[str]]   # category -> [val_at_pos_0, ..., val_at_pos_(cols-1)]
    clues: list[Clue] = field(default_factory=list)
    difficulty: str = "moderate"

    def position_of(self, category: str, value: str) -> int:
        """Return 0-indexed position of value in category."""
        return self.solution[category].index(value)


# ---------------------------------------------------------------------------
# CSP interface
# ---------------------------------------------------------------------------

def _build_csp(
    cols: int,
    categories: list[str],
    category_values: dict[str, list[str]],
    clues: list[Clue],
) -> CSP:
    variables = [f"{cat}:{val}"
                 for cat in categories
                 for val in category_values[cat]]
    csp = CSP(variables, cols)

    # All-different within each category
    for cat in categories:
        vals = category_values[cat]
        for i, v1 in enumerate(vals):
            for v2 in vals[i + 1:]:
                csp.add_constraint(
                    (f"{cat}:{v1}", f"{cat}:{v2}"),
                    lambda a, b: a != b
                )

    for clue in clues:
        _add_clue_constraint(csp, clue)

    return csp


def _add_clue_constraint(csp: CSP, clue: Clue):
    v1 = f"{clue.cat1}:{clue.val1}"

    if clue.clue_type == "position":
        pos = clue.position
        csp.add_constraint((v1,), lambda a, p=pos: a == p)

    elif clue.clue_type == "same_house":
        v2 = f"{clue.cat2}:{clue.val2}"
        csp.add_constraint((v1, v2), lambda a, b: a == b)

    elif clue.clue_type == "left_of":
        v2 = f"{clue.cat2}:{clue.val2}"
        csp.add_constraint((v1, v2), lambda a, b: a + 1 == b)

    elif clue.clue_type == "next_to":
        v2 = f"{clue.cat2}:{clue.val2}"
        csp.add_constraint((v1, v2), lambda a, b: abs(a - b) == 1)

    elif clue.clue_type == "not_same":
        v2 = f"{clue.cat2}:{clue.val2}"
        csp.add_constraint((v1, v2), lambda a, b: a != b)


def solve_puzzle(
    cols: int,
    categories: list[str],
    category_values: dict[str, list[str]],
    clues: list[Clue],
    max_solutions: int = 2,
) -> list[dict[str, int]]:
    """Return up to max_solutions CSP solutions (each maps 'cat:val' -> position)."""
    csp = _build_csp(cols, categories, category_values, clues)
    return csp.solve(max_solutions=max_solutions)


def has_unique_solution(
    cols: int,
    categories: list[str],
    category_values: dict[str, list[str]],
    clues: list[Clue],
) -> bool:
    return len(solve_puzzle(cols, categories, category_values, clues, 2)) == 1


# ---------------------------------------------------------------------------
# Solution generator
# ---------------------------------------------------------------------------

def generate_solution(
    cols: int,
    categories: list[str],
    rng: random.Random,
) -> dict[str, list[str]]:
    solution = {}
    for cat in categories:
        values = ATTRIBUTE_POOL[cat][:cols]
        shuffled = values[:]
        rng.shuffle(shuffled)
        solution[cat] = shuffled
    return solution


def category_values_from_solution(
    solution: dict[str, list[str]]
) -> dict[str, list[str]]:
    return {cat: list(vals) for cat, vals in solution.items()}


# ---------------------------------------------------------------------------
# Clue derivation
# ---------------------------------------------------------------------------

def generate_all_positive_clues(puzzle: Puzzle) -> list[Clue]:
    """Derive every true positive clue from the solution."""
    cols = puzzle.cols
    sol = puzzle.solution
    cats = puzzle.categories
    seen: set[Clue] = set()
    clues: list[Clue] = []

    def add(c: Clue):
        if c not in seen:
            seen.add(c)
            clues.append(c)

    for cat in cats:
        for val in sol[cat]:
            pos = puzzle.position_of(cat, val)  # 0-indexed

            # Position clue
            add(Clue("position", cat, val, position=pos + 1))

            # Same-house
            for other_cat in cats:
                if other_cat == cat:
                    continue
                other_val = sol[other_cat][pos]
                key = tuple(sorted([(cat, val), (other_cat, other_val)]))
                add(Clue("same_house", key[0][0], key[0][1], key[1][0], key[1][1]))

            # Left-of
            if pos + 1 < cols:
                for other_cat in cats:
                    other_val = sol[other_cat][pos + 1]
                    add(Clue("left_of", cat, val, other_cat, other_val))

            # Next-to
            for neighbor in [pos - 1, pos + 1]:
                if 0 <= neighbor < cols:
                    for other_cat in cats:
                        if other_cat == cat:
                            continue
                        other_val = sol[other_cat][neighbor]
                        key = tuple(sorted([(cat, val), (other_cat, other_val)]))
                        add(Clue("next_to", key[0][0], key[0][1], key[1][0], key[1][1]))

    return clues


def generate_not_same_clues(puzzle: Puzzle) -> list[Clue]:
    """Derive negative clues."""
    sol = puzzle.solution
    cats = puzzle.categories
    seen: set[Clue] = set()
    clues: list[Clue] = []

    for cat in cats:
        for val in sol[cat]:
            pos = puzzle.position_of(cat, val)
            for other_cat in cats:
                if other_cat == cat:
                    continue
                for other_val in sol[other_cat]:
                    other_pos = puzzle.position_of(other_cat, other_val)
                    if pos != other_pos:
                        key = tuple(sorted([(cat, val), (other_cat, other_val)]))
                        c = Clue("not_same", key[0][0], key[0][1], key[1][0], key[1][1])
                        if c not in seen:
                            seen.add(c)
                            clues.append(c)
    return clues


# ---------------------------------------------------------------------------
# Clue selection
# ---------------------------------------------------------------------------

def _select_minimal_clues(
    puzzle: Puzzle,
    pool: list[Clue],
    rng: random.Random,
) -> list[Clue]:
    """
    Greedy + prune approach:
    1. Shuffle pool.
    2. Add clues one-by-one until the solution becomes unique.
    3. Prune any clue whose removal still leaves a unique solution.
    """
    cols = puzzle.cols
    cats = puzzle.categories
    cv = category_values_from_solution(puzzle.solution)

    shuffled = list(pool)
    rng.shuffle(shuffled)

    selected: list[Clue] = []
    for clue in shuffled:
        if has_unique_solution(cols, cats, cv, selected + [clue]):
            selected.append(clue)
            break
        selected.append(clue)
        if has_unique_solution(cols, cats, cv, selected):
            break

    if not has_unique_solution(cols, cats, cv, selected):
        return []

    # Pruning pass
    for clue in list(reversed(selected)):
        candidate = [c for c in selected if c is not clue]
        if has_unique_solution(cols, cats, cv, candidate):
            selected = candidate

    return selected


def _extras_for_difficulty(difficulty: str, cols: int, rows: int) -> int:
    base = cols * rows
    if difficulty == "easy":
        return max(5, base // 3)
    if difficulty == "moderate":
        return max(2, base // 7)
    return 0


def clue_allowance(difficulty: str, cols: int, rows: int) -> int:
    base = cols * rows
    if difficulty == "easy":
        return max(3, base // 4)
    if difficulty == "moderate":
        return max(1, base // 8)
    return 0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_puzzle(
    grid: str = "4x5",
    difficulty: str = "moderate",
    seed: Optional[int] = None,
) -> Puzzle:
    """
    Generate a zebra puzzle with a guaranteed unique solution.

    Parameters
    ----------
    grid : str
        One of "3x4", "3x5", "4x4", "4x5", "4x6", "4x7"
        Format: <rows>x<cols>
          rows = # attribute categories
          cols = # houses/positions
    difficulty : str
        "easy" | "moderate" | "challenging"
    seed : int, optional
        For reproducibility.

    Returns
    -------
    Puzzle
    """
    if grid not in VALID_GRIDS:
        raise ValueError(f"grid must be one of {VALID_GRIDS}, got {grid!r}")
    if difficulty not in VALID_DIFFICULTIES:
        raise ValueError(f"difficulty must be one of {VALID_DIFFICULTIES}, got {difficulty!r}")

    rows, cols = map(int, grid.split("x"))
    rng = random.Random(seed)
    categories = CATEGORY_ORDER[:rows]

    for _attempt in range(30):
        solution = generate_solution(cols, categories, rng)
        puzzle = Puzzle(
            cols=cols,
            rows=rows,
            categories=categories,
            solution=solution,
            difficulty=difficulty,
        )

        all_positive = generate_all_positive_clues(puzzle)
        all_negative = generate_not_same_clues(puzzle)
        full_pool = all_positive + all_negative

        minimal = _select_minimal_clues(puzzle, full_pool, rng)
        if not minimal:
            continue

        # Pad with extra hints for easier difficulties
        extras_needed = _extras_for_difficulty(difficulty, cols, rows)
        if extras_needed > 0:
            minimal_set = set(minimal)
            extra_pool = [c for c in all_positive if c not in minimal_set]
            rng.shuffle(extra_pool)
            minimal.extend(extra_pool[:extras_needed])

        rng.shuffle(minimal)
        puzzle.clues = minimal
        return puzzle

    raise RuntimeError(
        f"Failed to generate a valid puzzle for grid={grid!r} after 30 attempts."
    )
