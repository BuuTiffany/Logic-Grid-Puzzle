from django.db import models
from django.contrib.auth.models import User

class PuzzleScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    puzzle_id = models.CharField(max_length=100)
    solve_time = models.FloatField()
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['solve_time']