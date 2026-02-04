from django.db import models
from django.contrib.auth.models import User
import uuid

class Problems(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')])
    input_format = models.TextField(default="No format provided")
    output_format = models.TextField(default="No format provided")
    samples = models.JSONField(default=list)
    explanation = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class Battle(models.Model):
    STATUS_CHOICES = [('live', 'Live'), ('done', 'Done')]
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4, editable=False)
    user_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name='battle_a')
    user_b = models.ForeignKey(User, on_delete=models.CASCADE, related_name='battle_b')
    problem = models.ForeignKey(Problems, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='live')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='battles_won')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

class MatchmakingTicket(models.Model):
    STATUS_CHOICES = [('waiting', 'Waiting'), ('matched', 'Matched'), ('canceled', 'Canceled')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket_id = models.CharField(max_length=36)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    battle = models.ForeignKey(Battle, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)