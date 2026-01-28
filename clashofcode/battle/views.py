from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
import uuid
from django.utils import timezone
from .models import MatchmakingTicket, Battle

# Create your views here.
def matchmaking():
    queue = MatchmakingTicket.objects.filter(status= "waiting").order_by("created_at")  

    while queue.count() > 2:
        user_a_ticket = queue[0]
        user_b_ticket = queue[1]

        battle = Battle.objects.create(
            
        )