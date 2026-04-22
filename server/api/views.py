from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
 
from api.services.puzzle_service import (
    get_or_generate,
    validate_solution,
    get_hint,
)
from api.puzzles.generator import VALID_GRIDS, VALID_DIFFICULTIES

@api_view(['GET'])
def hello(request):
    return Response({"message": "Hello from Django!"})

@api_view(['GET'])
def getLeaderboard(request):
    return Response({"message": "Leaderboard endpoint."})

@api_view(['GET'])
def getPuzzle(request):
    grid = request.query_params.get("grid", "4x5")
    difficulty = request.query_params.get("difficulty", "moderate")
 
    if grid not in VALID_GRIDS:
        return Response(
            {"error": f"Invalid grid {grid!r}. Must be one of {sorted(VALID_GRIDS)}."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if difficulty not in VALID_DIFFICULTIES:
        return Response(
            {"error": f"Invalid difficulty {difficulty!r}. Must be one of {sorted(VALID_DIFFICULTIES)}."},
            status=status.HTTP_400_BAD_REQUEST,
        )
 
    try:
        puzzle = get_or_generate(grid=grid, difficulty=difficulty)
    except Exception as e:
        return Response(
            {"error": "Failed to retrieve puzzle.", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
 
    return Response(puzzle, status=status.HTTP_200_OK)

@api_view(["POST"])
def validatePuzzle(request, puzzle_id: str):
    user_solution = request.data.get("solution")
 
    if not user_solution or not isinstance(user_solution, dict):
        return Response(
            {"error": "Request body must include a 'solution' object."},
            status=status.HTTP_400_BAD_REQUEST,
        )
 
    try:
        correct = validate_solution(puzzle_id, user_solution)
    except ValueError:
        return Response(
            {"error": f"Puzzle {puzzle_id!r} not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"error": "Validation failed.", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
 
    return Response({"correct": correct}, status=status.HTTP_200_OK)

@api_view(['GET'])
def getHint(request, puzzle_id: str):
    category = request.query_params.get("category")
    position = request.query_params.get("position")
 
    if not category:
        return Response(
            {"error": "Query param 'category' is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if position is None:
        return Response(
            {"error": "Query param 'position' is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
 
    try:
        position = int(position)
    except ValueError:
        return Response(
            {"error": "'position' must be an integer."},
            status=status.HTTP_400_BAD_REQUEST,
        )
 
    value = get_hint(puzzle_id, category, position)
 
    if value is None:
        return Response(
            {"error": "Puzzle not found or position/category out of range."},
            status=status.HTTP_404_NOT_FOUND,
        )
 
    return Response(
        {"category": category, "position": position, "value": value},
        status=status.HTTP_200_OK,
    )