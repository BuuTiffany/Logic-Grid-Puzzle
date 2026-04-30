from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user_id', related_name='profile')
    display_username = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'
        managed = False


class Solve(models.Model):
    puzzle_id    = models.UUIDField()
    username     = models.CharField(max_length=150)
    grid         = models.CharField(max_length=10)
    difficulty   = models.CharField(max_length=20)
    solve_time   = models.PositiveIntegerField()  # seconds
    completed_at = models.DateTimeField(auto_now_add=True)
    user         = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, db_column='user_id')

    class Meta:
        db_table = 'solves'
        ordering = ['solve_time']
        managed  = False  # table is created/owned by Supabase
