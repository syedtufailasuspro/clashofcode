from collections import deque

queue_data = deque()

def joinQueue(user_id):
    queue_data.append(user_id)

def leaveQueue(user_id):
    try:
        queue_data.remove(user_id)
    except ValueError:
        pass

def getQueue_size():
    return len(queue_data)

def pop_pair():
    user_a = queue_data.popleft() if queue_data else None
    user_b = queue_data.popleft() if queue_data else None
    return (user_a, user_b) if user_a and user_b else (None, None)