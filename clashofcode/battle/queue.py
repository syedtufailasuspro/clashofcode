import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)
QUEUE_KEY = 'matchmaking:queue'

def join_queue(user_id):
    """Add user to queue."""
    r.lpush(QUEUE_KEY, user_id)

def leave_queue(user_id):
    """Remove user from queue."""
    r.lrem(QUEUE_KEY, 0, user_id)

def get_queue_size():
    """Get queue length."""
    return r.llen(QUEUE_KEY)

def pop_pair():
    """Pop two users from queue (FIFO)."""
    user_a = r.rpop(QUEUE_KEY)
    user_b = r.rpop(QUEUE_KEY)
    return (user_a, user_b) if user_a and user_b else (None, None)