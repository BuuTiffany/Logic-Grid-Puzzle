from django.db import models


class Solve(models.Model):
    puzzle_id    = models.UUIDField()
    username     = models.CharField(max_length=150)
    grid         = models.CharField(max_length=10)
    difficulty   = models.CharField(max_length=20)
    solve_time   = models.PositiveIntegerField()  # seconds
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'solves'
        ordering = ['solve_time']
        managed  = False  # table is created/owned by Supabase