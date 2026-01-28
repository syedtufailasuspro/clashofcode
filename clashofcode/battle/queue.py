try:
    import redis
    r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=1)
    r.ping()  # Test connection
    USE_REDIS = True
except:
    USE_REDIS = False
    queue_data = []  # In-memory fallback

QUEUE_KEY = 'matchmaking:queue'

def joinQueue(user_id):
    if USE_REDIS:
        r.lpush(QUEUE_KEY, user_id)
    else:
        queue_data.append(user_id)

def leaveQueue(user_id):
    if USE_REDIS:
        r.lrem(QUEUE_KEY, 0, user_id)
    else:
        if user_id in queue_data:
            queue_data.remove(user_id)

def getQueue_size():
    if USE_REDIS:
        return r.llen(QUEUE_KEY)
    else:
        return len(queue_data)

def pop_pair():
    if USE_REDIS:
        user_a = r.rpop(QUEUE_KEY)
        user_b = r.rpop(QUEUE_KEY)
    else:
        user_a = queue_data.pop() if queue_data else None
        user_b = queue_data.pop() if queue_data else None
    return (user_a, user_b) if user_a and user_b else (None, None)