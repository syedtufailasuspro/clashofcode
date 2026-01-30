from django.db import models
from django.contrib.auth.models import User
import uuid

class Battle(models.Model):
    STATUS_CHOICES = [('live', 'Live'), ('done', 'Done')]
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4, editable=False)
    user_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name='battle_a')
    user_b = models.ForeignKey(User, on_delete=models.CASCADE, related_name='battle_b')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='live')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='battles_won')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

class Problems(models.Model):
    title = models.CharField(max_length=255)
    statement = models.TextField()
    difficulty = models.CharField(max_length=10, choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')])
    test_input_path = models.TextField(max_length=255)
    test_output_path = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class Submissions(models.Model):
    VERDICT_CHOICES = [('AC', 'Accepted'), ('WA', 'Wrong Answer'), ('TLE', 'Time Limit'), ('CE', 'Compile Error')]
    problem = models.ForeignKey(Problems, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=20, default='python')
    verdict = models.CharField(max_length=3, choices=VERDICT_CHOICES, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

class MatchmakingTicket(models.Model):
    STATUS_CHOICES = [('waiting', 'Waiting'), ('matched', 'Matched'), ('canceled', 'Canceled')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket_id = models.CharField(max_length=36)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    battle = models.ForeignKey(Battle, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)