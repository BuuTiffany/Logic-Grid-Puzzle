import json
import re
import secrets
import uuid as _uuid
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework import status

from api.models import UserProfile
from api.services.puzzle_service import (
    get_or_generate,
    validate_solution,
    get_hint,
    get_leaderboard,
    get_global_stats,
    get_profile,
    submit_solve,
)
from api.puzzles.generator import VALID_GRIDS, VALID_DIFFICULTIES

_USERNAME_RE = re.compile(r'^[\w\s\-\.]+$')   # letters, digits, _, space, hyphen, dot
_MAX_USERNAME = 30
_MAX_SOLVE_TIME = 86_400                       # 24 h ceiling
_MAX_EMAIL = 254
_MAX_PASSWORD = 128
_GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
_GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


def _clean_text(value, max_length: int, trim: bool = True) -> str:
    value = str(value or "")
    value = "".join(ch for ch in value if ch.isprintable())
    if trim:
        value = value.strip()
    return value[:max_length]


def _clean_username(value) -> str:
    return re.sub(r'\s+', ' ', _clean_text(value, _MAX_USERNAME))


def _clean_email(value) -> str:
    return _clean_text(value, _MAX_EMAIL).lower()


def _clean_password(value) -> str:
    return _clean_text(value, _MAX_PASSWORD, trim=False)


def _profile_username(user) -> str | None:
    try:
        return user.profile.display_username
    except UserProfile.DoesNotExist:
        return None


def _auth_payload(user) -> dict:
    username = _profile_username(user)
    return {
        "authenticated": True,
        "id": user.id,
        "email": user.email,
        "username": username,
        "needs_username": username is None,
    }


def _invalid_credentials():
    return Response({"error": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)


def _frontend_redirect(params: dict[str, str]):
    base = settings.FRONTEND_URL.rstrip("/")
    query = urlencode(params)
    return f"{base}/?{query}" if query else f"{base}/"


def _google_redirect_uri(request) -> str:
    if settings.BACKEND_URL:
        return f"{settings.BACKEND_URL.rstrip('/')}/api/auth/google/callback/"
    return request.build_absolute_uri("/api/auth/google/callback/")


def _post_form_json(url: str, data: dict) -> tuple[int, dict]:
    body = urlencode(data).encode("utf-8")
    request = Request(url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        return e.code, {}
    except (URLError, TimeoutError, json.JSONDecodeError):
        return 0, {}


def _get_json(url: str, params: dict) -> tuple[int, dict]:
    try:
        with urlopen(f"{url}?{urlencode(params)}", timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        return e.code, {}
    except (URLError, TimeoutError, json.JSONDecodeError):
        return 0, {}


@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def signup(request):
    email = _clean_email(request.data.get("email"))
    password = _clean_password(request.data.get("password"))

    try:
        validate_email(email)
    except ValidationError:
        return Response({"error": "Invalid email."}, status=status.HTTP_400_BAD_REQUEST)

    if len(password) < 8:
        return Response({"error": "Password must be at least 8 characters."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email__iexact=email).exists():
        return Response({"error": "An account with that email already exists."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.create_user(
            username=f"account_{_uuid.uuid4().hex[:24]}",
            email=email,
            password=password,
        )
    except IntegrityError:
        return Response({"error": "Could not create account."}, status=status.HTTP_400_BAD_REQUEST)

    login(request, user)
    return Response(_auth_payload(user), status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def loginUser(request):
    email = _clean_email(request.data.get("email"))
    password = _clean_password(request.data.get("password"))

    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        return _invalid_credentials()

    authed = authenticate(request, username=user.username, password=password)
    if authed is None:
        return _invalid_credentials()

    login(request, authed)
    return Response(_auth_payload(authed), status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def logoutUser(request):
    logout(request)
    return Response({"authenticated": False}, status=status.HTTP_200_OK)


@api_view(['GET'])
def googleStart(request):
    if not settings.GOOGLE_OAUTH_CLIENT_ID or not settings.GOOGLE_OAUTH_CLIENT_SECRET:
        return Response({"error": "Google OAuth is not configured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    state = secrets.token_urlsafe(32)
    request.session["google_oauth_state"] = state
    params = {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "redirect_uri": _google_redirect_uri(request),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }
    from django.shortcuts import redirect
    return redirect(f"{_GOOGLE_AUTH_URL}?{urlencode(params)}")


@api_view(['GET'])
def googleCallback(request):
    from django.shortcuts import redirect

    code = request.query_params.get("code")
    state = request.query_params.get("state")
    expected_state = request.session.pop("google_oauth_state", None)

    if not code or not state or state != expected_state:
        return redirect(_frontend_redirect({"auth_error": "google"}))

    token_status, token_data = _post_form_json(
        _GOOGLE_TOKEN_URL,
        {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": _google_redirect_uri(request),
            "grant_type": "authorization_code",
        },
    )
    if token_status != 200:
        return redirect(_frontend_redirect({"auth_error": "google"}))

    id_token = token_data.get("id_token")
    tokeninfo_status, tokeninfo = _get_json(_GOOGLE_TOKENINFO_URL, {"id_token": id_token})
    if tokeninfo_status != 200:
        return redirect(_frontend_redirect({"auth_error": "google"}))

    email = _clean_email(tokeninfo.get("email"))
    if tokeninfo.get("aud") != settings.GOOGLE_OAUTH_CLIENT_ID or tokeninfo.get("email_verified") not in ("true", True):
        return redirect(_frontend_redirect({"auth_error": "google"}))

    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        user = User(username=f"account_{_uuid.uuid4().hex[:24]}", email=email)
        user.set_unusable_password()
        user.save()

    login(request, user)
    needs_username = _profile_username(user) is None
    return redirect(_frontend_redirect({"auth": "google", "needs_username": "1" if needs_username else "0"}))


@api_view(['GET'])
def getCurrentUser(request):
    if not request.user.is_authenticated:
        return Response({"authenticated": False, "username": None, "needs_username": False}, status=status.HTTP_200_OK)
    return Response(_auth_payload(request.user), status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def setUsername(request):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

    username = _clean_username(request.data.get("username"))
    if not username:
        return Response({"error": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)

    if len(username) > _MAX_USERNAME or not _USERNAME_RE.match(username):
        return Response({"error": "Invalid username."}, status=status.HTTP_400_BAD_REQUEST)

    taken = UserProfile.objects.filter(display_username__iexact=username).exclude(user=request.user).exists()
    if taken:
        return Response({"error": "Username is already taken."}, status=status.HTTP_400_BAD_REQUEST)

    profile, _ = UserProfile.objects.update_or_create(
        user=request.user,
        defaults={"display_username": username},
    )
    return Response({**_auth_payload(request.user), "username": profile.display_username, "needs_username": False}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def submitSolve(request):
    username   = _clean_username(request.data.get("username", ""))
    puzzle_id  = str(request.data.get("puzzle_id",  "")).strip()
    grid       = str(request.data.get("grid",       "")).strip()
    difficulty = str(request.data.get("difficulty", "")).strip().lower()
    solve_time = request.data.get("solve_time")
    user_id = None

    if request.user.is_authenticated:
        username = _profile_username(request.user)
        user_id = request.user.id
        if not username:
            return Response({"error": "Account username is required."}, status=status.HTTP_400_BAD_REQUEST)

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
        submit_solve(puzzle_id, username, grid, difficulty, solve_time, user_id)
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
def getStats(request):
    try:
        stats = get_global_stats(User.objects.count())
    except Exception as e:
        return Response(
            {"error": "Failed to fetch stats.", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['GET'])
def getProfile(request):
    if not request.user.is_authenticated:
        return Response(
            {"error": "Authentication required."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    username = _profile_username(request.user)
    if not username:
        return Response(
            {"error": "Account username is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        solves = get_profile(request.user.id)
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
