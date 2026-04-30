from django.urls import path
from . import views

urlpatterns = [
    path('auth/signup/', views.signup),
    path('auth/login/', views.loginUser),
    path('auth/logout/', views.logoutUser),
    path('auth/me/', views.getCurrentUser),
    path('auth/username/', views.setUsername),
    path('auth/google/start/', views.googleStart),
    path('auth/google/callback/', views.googleCallback),
    path('hello/', views.hello),
    path('leaderboard/', views.getLeaderboard),
    path('stats/', views.getStats),
    path('profile/', views.getProfile),
    path('solves/', views.submitSolve),
    path('puzzle/', views.getPuzzle),
    path('puzzle/<str:puzzle_id>/validate/', views.validatePuzzle),
    path('puzzle/<str:puzzle_id>/hint/', views.getHint),
]
