"""
Lightweight backtracking CSP solver for zebra puzzles.
No external dependencies — pure Python.
"""

from __future__ import annotations
from typing import Callable


class CSP:
    """
    Variables have integer domains [1..N].
    Constraints are binary or unary callables (var_name, ...) -> bool.
    """

    def __init__(self, variables: list[str], domain_size: int):
        self.variables = variables
        self.domain_size = domain_size
        # constraints: list of (tuple_of_var_names, callable(*values)->bool)
        self.constraints: list[tuple[tuple[str, ...], Callable]] = []
        self._var_index = {v: i for i, v in enumerate(variables)}

    def add_constraint(self, var_names: tuple[str, ...], fn: Callable):
        self.constraints.append((var_names, fn))

    def solve(self, max_solutions: int = 2) -> list[dict[str, int]]:
        """Return up to max_solutions solutions."""
        assignment: dict[str, int] = {}
        solutions: list[dict[str, int]] = []
        self._backtrack(assignment, solutions, max_solutions)
        return solutions

    # ── private ──────────────────────────────────────────────────────────────

    def _backtrack(
        self,
        assignment: dict[str, int],
        solutions: list[dict[str, int]],
        max_solutions: int,
    ) -> bool:
        if len(solutions) >= max_solutions:
            return True

        unassigned = [v for v in self.variables if v not in assignment]
        if not unassigned:
            solutions.append(dict(assignment))
            return len(solutions) >= max_solutions

        var = self._select_variable(unassigned, assignment)
        domain = self._order_domain(var, assignment)

        for value in domain:
            assignment[var] = value
            if self._is_consistent(var, assignment):
                result = self._backtrack(assignment, solutions, max_solutions)
                if result:
                    return True
            del assignment[var]

        return False

    def _select_variable(
        self, unassigned: list[str], assignment: dict[str, int]
    ) -> str:
        """MRV heuristic: pick variable with fewest remaining legal values."""
        def remaining_values(v: str) -> int:
            return sum(
                1 for val in range(1, self.domain_size + 1)
                if self._would_be_consistent(v, val, assignment)
            )

        return min(unassigned, key=remaining_values)

    def _order_domain(self, var: str, assignment: dict[str, int]) -> list[int]:
        return list(range(1, self.domain_size + 1))

    def _is_consistent(self, var: str, assignment: dict[str, int]) -> bool:
        for var_names, fn in self.constraints:
            if var not in var_names:
                continue
            # Check only if all variables in this constraint are assigned
            if not all(v in assignment for v in var_names):
                continue
            values = tuple(assignment[v] for v in var_names)
            if not fn(*values):
                return False
        return True

    def _would_be_consistent(
        self, var: str, value: int, assignment: dict[str, int]
    ) -> bool:
        tmp = dict(assignment)
        tmp[var] = value
        return self._is_consistent(var, tmp)
