"""
Tests for api/services/puzzle_service.py

These tests mock the Supabase client so no real DB connection is needed.
Run with: python manage.py test api.tests.test_puzzle_service
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch
from django.test import TestCase

from api.services.puzzle_service import (
    generate_and_store,
    fetch_puzzle_private,
    get_or_generate,
    validate_solution,
    get_hint,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

MOCK_SOLUTION = {
    "color":       ["Red", "Blue", "Green", "Yellow", "White"],
    "nationality": ["English", "Spanish", "Ukrainian", "Norwegian", "Japanese"],
    "drink":       ["Coffee", "Tea", "Milk", "Water", "OrangeJuice"],
    "pet":         ["Dog", "Snail", "Fox", "Horse", "Zebra"],
}

MOCK_ROW = {
    "id":         "test-uuid-1234",
    "grid":       "4x5",
    "difficulty": "moderate",
    "seed":       42,
    "categories": list(MOCK_SOLUTION.keys()),
    "clues":      [{"id": 1, "type": "same_house", "text": "The person with Red also has Coffee."}],
    "solution":   MOCK_SOLUTION,
    "used":       False,
}


def _make_supabase_mock(data: list | dict | None):
    """Return a mock Supabase client whose table() chain resolves to data."""
    mock_response = MagicMock()
    mock_response.data = data

    mock_table = MagicMock()
    # Chain: .table().select().eq()...execute() all return mock_response
    mock_table.select.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.update.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.order.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.maybe_single.return_value = mock_table
    mock_table.execute.return_value = mock_response

    mock_client = MagicMock()
    mock_client.table.return_value = mock_table
    return mock_client, mock_response


# ---------------------------------------------------------------------------
# generate_and_store
# ---------------------------------------------------------------------------

class TestGenerateAndStore(TestCase):

    @patch("api.services.puzzle_service._client")
    def test_returns_public_dict_with_id(self, mock_get_client):
        mock_client, mock_response = _make_supabase_mock([{"id": "abc-123"}])
        mock_get_client.return_value = mock_client

        result = generate_and_store(grid="4x5", difficulty="moderate", seed=42)

        self.assertIn("id", result)
        self.assertEqual(result["id"], "abc-123")
        self.assertNotIn("solution", result)

    @patch("api.services.puzzle_service._client")
    def test_solution_not_in_public_result(self, mock_get_client):
        mock_client, _ = _make_supabase_mock([{"id": "abc-123"}])
        mock_get_client.return_value = mock_client

        result = generate_and_store(grid="3x4", difficulty="easy", seed=1)
        self.assertNotIn("solution", result)

    @patch("api.services.puzzle_service._client")
    def test_raises_on_empty_supabase_response(self, mock_get_client):
        mock_client, _ = _make_supabase_mock([])   # empty data
        mock_get_client.return_value = mock_client

        with self.assertRaises(RuntimeError):
            generate_and_store(grid="4x5", difficulty="moderate", seed=1)


# ---------------------------------------------------------------------------
# fetch_puzzle_private
# ---------------------------------------------------------------------------

class TestFetchPuzzlePrivate(TestCase):

    @patch("api.services.puzzle_service._client")
    def test_returns_full_row_including_solution(self, mock_get_client):
        mock_client, _ = _make_supabase_mock(MOCK_ROW)
        mock_get_client.return_value = mock_client

        result = fetch_puzzle_private("test-uuid-1234")
        self.assertIn("solution", result)
        self.assertEqual(result["solution"], MOCK_SOLUTION)

    @patch("api.services.puzzle_service._client")
    def test_returns_none_if_not_found(self, mock_get_client):
        mock_client, _ = _make_supabase_mock(None)
        mock_get_client.return_value = mock_client

        result = fetch_puzzle_private("nonexistent-id")
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# get_or_generate
# ---------------------------------------------------------------------------

class TestGetOrGenerate(TestCase):

    @patch("api.services.puzzle_service._client")
    def test_serves_from_pool_when_available(self, mock_get_client):
        mock_client, mock_response = _make_supabase_mock([MOCK_ROW])
        mock_get_client.return_value = mock_client

        result = get_or_generate(grid="4x5", difficulty="moderate")

        self.assertEqual(result["id"], MOCK_ROW["id"])
        self.assertNotIn("solution", result)

    @patch("api.services.puzzle_service.generate_and_store")
    @patch("api.services.puzzle_service._client")
    def test_falls_back_to_generation_when_pool_empty(self, mock_get_client, mock_generate):
        mock_client, _ = _make_supabase_mock([])   # empty pool
        mock_get_client.return_value = mock_client
        mock_generate.return_value = {"id": "fresh-uuid", "grid": "4x5"}

        result = get_or_generate(grid="4x5", difficulty="moderate")

        mock_generate.assert_called_once_with(grid="4x5", difficulty="moderate")
        self.assertEqual(result["id"], "fresh-uuid")


# ---------------------------------------------------------------------------
# validate_solution
# ---------------------------------------------------------------------------

class TestValidateSolution(TestCase):

    @patch("api.services.puzzle_service.fetch_puzzle_private")
    def test_correct_solution_returns_true(self, mock_fetch):
        mock_fetch.return_value = MOCK_ROW
        self.assertTrue(validate_solution("test-uuid-1234", MOCK_SOLUTION))

    @patch("api.services.puzzle_service.fetch_puzzle_private")
    def test_wrong_solution_returns_false(self, mock_fetch):
        mock_fetch.return_value = MOCK_ROW
        wrong = dict(MOCK_SOLUTION)
        wrong["color"] = ["Blue", "Red", "Green", "Yellow", "White"]  # swapped
        self.assertFalse(validate_solution("test-uuid-1234", wrong))

    @patch("api.services.puzzle_service.fetch_puzzle_private")
    def test_raises_value_error_if_not_found(self, mock_fetch):
        mock_fetch.return_value = None
        with self.assertRaises(ValueError):
            validate_solution("bad-id", MOCK_SOLUTION)


# ---------------------------------------------------------------------------
# get_hint
# ---------------------------------------------------------------------------

class TestGetHint(TestCase):

    @patch("api.services.puzzle_service.fetch_puzzle_private")
    def test_returns_correct_value(self, mock_fetch):
        mock_fetch.return_value = MOCK_ROW
        # position 0, category "color" → "Red"
        result = get_hint("test-uuid-1234", "color", 0)
        self.assertEqual(result, "Red")

    @patch("api.services.puzzle_service.fetch_puzzle_private")
    def test_returns_none_for_out_of_range_position(self, mock_fetch):
        mock_fetch.return_value = MOCK_ROW
        result = get_hint("test-uuid-1234", "color", 99)
        self.assertIsNone(result)

    @patch("api.services.puzzle_service.fetch_puzzle_private")
    def test_returns_none_if_puzzle_not_found(self, mock_fetch):
        mock_fetch.return_value = None
        result = get_hint("bad-id", "color", 0)
        self.assertIsNone(result)

    @patch("api.services.puzzle_service.fetch_puzzle_private")
    def test_returns_none_for_invalid_category(self, mock_fetch):
        mock_fetch.return_value = MOCK_ROW
        result = get_hint("test-uuid-1234", "nonexistent_category", 0)
        self.assertIsNone(result)