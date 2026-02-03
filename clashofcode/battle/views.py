from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import uuid
from django.utils import timezone
from .models import MatchmakingTicket, Battle, Problems
from .models import Battle
import uuid
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Max, Min
import random
from celery import shared_task
import time
from .tasks import run_matchmaking

# Create your views here.

@login_required(login_url='login')
def join_queue(request):
    user = request.user
    
    # Cleanup matched tickets
    MatchmakingTicket.objects.filter(user=user, status='matched').delete()

    #ticket
    if MatchmakingTicket.objects.filter(user=user, status='waiting').exists():
        return render(request, "battle/queue.html", {})
    
    ticket = MatchmakingTicket.objects.create(
        user=user,
        ticket_id = uuid.uuid4()
    )
    
    return render(request, "battle/queue.html", {})

@login_required(login_url='login')
def leave_queue(request):
    user = request.user
    
    ticket = MatchmakingTicket.objects.filter(user=user, status='waiting').first()

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



@login_required(login_url='login')
def battle_status(request):
    ticket = MatchmakingTicket.objects.filter(user=request.user).first()
    if ticket and ticket.status == 'matched':
        return JsonResponse({
            'status': 'found',
            'battle_id': ticket.battle.id,
            'redirect_url': f'/battle/battle_arena/{ticket.battle.id}/'
        })

    else:
        return JsonResponse({
            'status': 'not found'
        })


@login_required(login_url='login')
def acknowledge_match(request, battle_id):
    #Called when player receives the redirect and is about to navigate to arena
    user = request.user
    
    ticket = MatchmakingTicket.objects.filter(user=user, battle_id=battle_id).first()

    if not ticket:
        return JsonResponse({'error': 'Invalid battle match'}, status=400)
    
    # Delete the ticket - player is now in battle
    ticket.delete()
    
    return JsonResponse({'status': 'acknowledged'})



def battle_arena(request,battle_id):
    battle = Battle.objects.filter(id=battle_id).first()
    if not battle:
        return HttpResponse("Battle does not exist")
    
    if battle.status in ('done', 'Done'):
        return HttpResponse("Battle is done for. Go find a job")
    
    question = battle.problem

    return render(request,'battle/index.html',{'battle_id':battle_id, 'question':question})




