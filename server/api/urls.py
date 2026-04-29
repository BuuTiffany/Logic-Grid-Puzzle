from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello),
    path('leaderboard/', views.getLeaderboard),
    path('profile/', views.getProfile),
    path('solves/', views.submitSolve),
    path('puzzle/', views.getPuzzle),
    path('puzzle/<str:puzzle_id>/validate/', views.validatePuzzle),
    path('puzzle/<str:puzzle_id>/hint/', views.getHint),
]