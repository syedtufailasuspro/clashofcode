from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
import uuid
from django.utils import timezone
from .models import MatchmakingTicket, Battle
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .queue import join_queue, leave_queue, get_queue_size
from .models import Battle
import uuid
from django.contrib.auth.decorators import login_required


# Create your views here.
def join_queue(request):
    user = request.user
    if not user.is_authenticated:
        return redirect("login")
    
    #ticket
    ticket = MatchmakingTicket.objects.create(
        user=user,
        ticket_id = uuid.uuid4()
    )
    
    return HttpResponse("queue joined. waiting for players...")

def leave_queue(request):
    return HttpResponse("queue left. redirecting back...")

