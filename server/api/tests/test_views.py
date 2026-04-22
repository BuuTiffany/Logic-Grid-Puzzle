"""
Tests for api/views.py
Run with: python manage.py test api.tests.test_views
"""

from __future__ import annotations

from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APIClient


MOCK_PUBLIC_PUZZLE = {
    "id":         "test-uuid-5678",
    "grid":       "4x5",
    "difficulty": "moderate",
    "categories": ["color", "nationality", "drink", "pet"],
    "num_clues":  12,
    "clues": [
        {
            "id": 1,
            "type": "same_house",
            "text": "The person with Red also has Coffee.",
            "cat1": "color",
            "val1": "Red",
            "cat2": "drink",
            "val2": "Coffee",
            "position": None,
        }
    ],
}

MOCK_SOLUTION = {
    "color":       ["Red", "Blue", "Green", "Yellow", "White"],
    "nationality": ["English", "Spanish", "Ukrainian", "Norwegian", "Japanese"],
    "drink":       ["Coffee", "Tea", "Milk", "Water", "OrangeJuice"],
    "pet":         ["Dog", "Snail", "Fox", "Horse", "Zebra"],
}


class TestHelloView(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_returns_200(self):
        res = self.client.get("/api/")
        self.assertEqual(res.status_code, 200)

    def test_returns_message(self):
        res = self.client.get("/api/")
        self.assertEqual(res.data["message"], "Hello from Django!")

# GET /api/puzzle/
class TestGetPuzzleView(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("api.views.get_or_generate", return_value=MOCK_PUBLIC_PUZZLE)
    def test_returns_200_with_default_params(self, _):
        res = self.client.get("/api/puzzle/")
        self.assertEqual(res.status_code, 200)

    @patch("api.views.get_or_generate", return_value=MOCK_PUBLIC_PUZZLE)
    def test_response_has_no_solution(self, _):
        res = self.client.get("/api/puzzle/")
        self.assertNotIn("solution", res.data)

    @patch("api.views.get_or_generate", return_value=MOCK_PUBLIC_PUZZLE)
    def test_passes_grid_and_difficulty_params(self, mock_service):
        self.client.get("/api/puzzle/?grid=3x4&difficulty=easy")
        mock_service.assert_called_once_with(grid="3x4", difficulty="easy")

    def test_invalid_grid_returns_400(self):
        res = self.client.get("/api/puzzle/?grid=9x9")
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.data)

    def test_invalid_difficulty_returns_400(self):
        res = self.client.get("/api/puzzle/?difficulty=impossible")
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.data)

    @patch("api.views.get_or_generate", side_effect=Exception("Supabase down"))
    def test_service_error_returns_500(self, _):
        res = self.client.get("/api/puzzle/")
        self.assertEqual(res.status_code, 500)
        self.assertIn("error", res.data)

# POST /api/puzzle/<id>/validate/
class TestValidatePuzzleView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/puzzle/test-uuid-5678/validate/"

    @patch("api.views.validate_solution", return_value=True)
    def test_correct_solution_returns_true(self, _):
        res = self.client.post(self.url, {"solution": MOCK_SOLUTION}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data["correct"])

    @patch("api.views.validate_solution", return_value=False)
    def test_wrong_solution_returns_false(self, _):
        res = self.client.post(self.url, {"solution": MOCK_SOLUTION}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.data["correct"])

    def test_missing_solution_body_returns_400(self):
        res = self.client.post(self.url, {}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_non_dict_solution_returns_400(self):
        res = self.client.post(self.url, {"solution": "wrong_type"}, format="json")
        self.assertEqual(res.status_code, 400)

    @patch("api.views.validate_solution", side_effect=ValueError("not found"))
    def test_unknown_puzzle_id_returns_404(self, _):
        res = self.client.post(self.url, {"solution": MOCK_SOLUTION}, format="json")
        self.assertEqual(res.status_code, 404)

# GET /api/puzzle/<id>/hint/
class TestGetHintView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/puzzle/test-uuid-5678/hint/"

    @patch("api.views.get_hint", return_value="Red")
    def test_returns_correct_value(self, _):
        res = self.client.get(self.url + "?category=color&position=0")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["value"], "Red")
        self.assertEqual(res.data["category"], "color")
        self.assertEqual(res.data["position"], 0)

    def test_missing_category_returns_400(self):
        res = self.client.get(self.url + "?position=0")
        self.assertEqual(res.status_code, 400)

    def test_missing_position_returns_400(self):
        res = self.client.get(self.url + "?category=color")
        self.assertEqual(res.status_code, 400)

    def test_non_integer_position_returns_400(self):
        res = self.client.get(self.url + "?category=color&position=abc")
        self.assertEqual(res.status_code, 400)

    @patch("api.views.get_hint", return_value=None)
    def test_out_of_range_returns_404(self, _):
        res = self.client.get(self.url + "?category=color&position=99")
        self.assertEqual(res.status_code, 404)