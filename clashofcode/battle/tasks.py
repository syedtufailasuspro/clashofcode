from celery import shared_task
from django.db import transaction
from .models import MatchmakingTicket, Battle, Problems
import logging

logger = logging.getLogger(__name__)

@shared_task
def run_matchmaking():
    """
    Look for waiting players and match them. 
    Runs automatically via Celery Beat.
    """
    # We loop a few times to clear the queue if many people are waiting,
    # but we don't loop forever.
    matches_made = 0
    
    # Try to match up to 10 pairs in one execution cycle
    for _ in range(10): 
        with transaction.atomic():
            # 1. Lock the table and get 2 waiting players
            tickets = list(
                MatchmakingTicket.objects.select_for_update(skip_locked=True)
                .filter(status='waiting')
                .order_by('created_at')[:2]
            )

            # If less than 2 players, stop trying
            if len(tickets) < 2:
                break
            
            ticket1 = tickets[0]
            ticket2 = tickets[1]

            # 2. Get a Problem
            problem = Problems.objects.order_by('?').first()
            if not problem:
                logger.error("Matchmaking failed: No problems in database")
                break

            # 3. Create the Battle
            battle = Battle.objects.create(
                user_a=ticket1.user,
                user_b=ticket2.user,
                problem=problem
            )

            # 4. Update Tickets to 'matched'
            ticket1.status = 'matched'
            ticket1.battle = battle
            ticket1.save()

            ticket2.status = 'matched'
            ticket2.battle = battle
            ticket2.save()

            matches_made += 1
            logger.info(f"Match created: {battle.id}")

    return f"Matchmaking cycle done. Matches made: {matches_made}"