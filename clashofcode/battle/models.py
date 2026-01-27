from django.db import models
from django.contrib.auth.models import User


class MatchmakingTicket(models.Model):
    STATUS_CHOICES = [('waiting', 'Waiting'), ('matched', 'Matched'), ('canceled', 'Canceled')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    created_at = models.DateTimeField(auto_now_add=True)


