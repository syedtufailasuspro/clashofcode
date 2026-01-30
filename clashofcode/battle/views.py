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
        return render(request, "battle/queue.html", {})
    
    ticket = MatchmakingTicket.objects.create(
        user=user,
        ticket_id = uuid.uuid4()
    )
    
    return render(request, "battle/queue.html", {})

@login_required(login_url='login')
def leave_queue(request):
    user = request.user
    
    ticket = MatchmakingTicket.objects.filter(user=user).first()

    if not ticket:
        return JsonResponse({'error': 'Not in queue'}, status=400)

    ticket.delete()


    return HttpResponse("queue left. redirecting back...")

@login_required(login_url='login')
def queue_status(request):
    queue_count = MatchmakingTicket.objects.filter(status = "waiting").count()

    if queue_count < 10:
        est_wait = "~10s"
    elif queue_count < 50:
        est_wait = "~30s"
    elif queue_count < 100:
        est_wait = "~1m"
    else:
        est_wait = "~2m"
    
    print(queue_count)
    return JsonResponse({
        'queue_count': queue_count,
        'est_wait': est_wait,
        'status': 'searching'
    })
