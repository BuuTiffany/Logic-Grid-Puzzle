from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello), # Wires to /backend/urls
    path('leaderboard/', views.getLeaderboard),
    path('puzzle/', views.getPuzzle),
    path('hint/', views.getHint),
]