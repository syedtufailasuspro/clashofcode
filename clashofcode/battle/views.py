from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
import uuid
from django.utils import timezone
from .models import MatchmakingTicket, Battle
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .queue import joinQueue, leaveQueue, getQueue_size
from .models import Battle
import uuid
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required(login_url='login')
def join_queue(request):
    user = request.user
    
    #ticket
    if MatchmakingTicket.objects.filter(user=user).exists():
        return HttpResponse("Already in queue")
    
    ticket = MatchmakingTicket.objects.create(
        user=user,
        ticket_id = uuid.uuid4()
    )
    
    joinQueue(ticket.ticket_id)
    return JsonResponse({'status': 'waiting', 'queue_size': getQueue_size()})

@login_required(login_url='login')
def leave_queue(request):
    user = request.user
    
    ticket = MatchmakingTicket.objects.filter(user=user).first()

    if not ticket:
        return JsonResponse({'error': 'Not in queue'}, status=400)

    leaveQueue(ticket.ticket_id)
    ticket.delete()


    return HttpResponse("queue left. redirecting back...")

