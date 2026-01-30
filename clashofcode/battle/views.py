from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import uuid
from django.utils import timezone
from .models import MatchmakingTicket, Battle
from .models import Battle
import uuid
from django.contrib.auth.decorators import login_required
from django.db import transaction


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


@login_required(login_url='login')
def battle_status(request):
    ticket = MatchmakingTicket.objects.filter(user=request.user).first()
    if ticket and ticket.status == 'matched':
        return JsonResponse({
            'status': 'found',
            'battle_id': ticket.battle.id,
            'redirect_url': f'/battle/{ticket.battle.id}/'
        })

    battle = join_match()

    if battle:
        return JsonResponse({
            'status': 'found',
            'battle_id': battle.id,
            'redirect_url': f'/battle/{battle.id}/'
        })
    else:
        return JsonResponse({
            'status': 'not found'
        })


def join_match():
    with transaction.atomic():
        playerTickets = MatchmakingTicket.objects.select_for_update().filter(status = 'waiting').order_by('created_at')[:2]
        
        if playerTickets.count() != 2:
            return None
    
        player1Ticket = playerTickets[0]
        player2Ticket = playerTickets[1]

        currBattle = Battle.objects.create(
            user_a = player1Ticket.user,
            user_b = player2Ticket.user,
        )

        #Update tickets with the battle ID
        player1Ticket.status = 'matched'
        player1Ticket.battle = currBattle # Add this field to your model
        player1Ticket.save()

        player2Ticket.status = 'matched'
        player2Ticket.battle = currBattle
        player2Ticket.save()

        return currBattle
        
            


