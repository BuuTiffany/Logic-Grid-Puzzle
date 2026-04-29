import re
import uuid as _uuid

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from api.services.puzzle_service import (
    get_or_generate,
    validate_solution,
    get_hint,
    get_leaderboard,
    get_profile,
    submit_solve,
)
from api.puzzles.generator import VALID_GRIDS, VALID_DIFFICULTIES

_USERNAME_RE = re.compile(r'^[\w\s\-\.]+$')   # letters, digits, _, space, hyphen, dot
_MAX_USERNAME = 30
_MAX_SOLVE_TIME = 86_400                       # 24 h ceiling

@api_view(['POST'])
def submitSolve(request):
    username   = str(request.data.get("username",   "")).strip()
    puzzle_id  = str(request.data.get("puzzle_id",  "")).strip()
    grid       = str(request.data.get("grid",       "")).strip()
    difficulty = str(request.data.get("difficulty", "")).strip().lower()
    solve_time = request.data.get("solve_time")

    # Empty username → skip silently, no DB write
    if not username:
        return Response({"saved": False}, status=status.HTTP_200_OK)

    if len(username) > _MAX_USERNAME or not _USERNAME_RE.match(username):
        return Response({"error": "Invalid username."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        _uuid.UUID(puzzle_id)
    except (ValueError, AttributeError):
        return Response({"error": "Invalid puzzle_id."}, status=status.HTTP_400_BAD_REQUEST)

    if grid not in VALID_GRIDS:
        return Response({"error": "Invalid grid."}, status=status.HTTP_400_BAD_REQUEST)

    if difficulty not in VALID_DIFFICULTIES:
        return Response({"error": "Invalid difficulty."}, status=status.HTTP_400_BAD_REQUEST)

    if not isinstance(solve_time, int) or solve_time <= 0 or solve_time > _MAX_SOLVE_TIME:
        return Response({"error": "Invalid solve_time."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        submit_solve(puzzle_id, username, grid, difficulty, solve_time)
    except Exception as e:
        return Response(
            {"error": "Failed to save solve.", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response({"saved": True}, status=status.HTTP_200_OK)


@api_view(['GET'])
def hello(request):
    return Response({"message": "Hello from Django!"})

@api_view(['GET'])
def getLeaderboard(request):
    try:
        players = get_leaderboard()
    except Exception as e:
        return Response(
            {"error": "Failed to fetch leaderboard.", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return Response({"players": players}, status=status.HTTP_200_OK)


@api_view(['GET'])
def getProfile(request):
    username = request.query_params.get("username", "")
    if not username:
        return Response(
            {"error": "Query param 'username' is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        solves = get_profile(username)
    except Exception as e:
        return Response(
            {"error": "Failed to fetch profile.", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return Response({"username": username, "solves": solves}, status=status.HTTP_200_OK)

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