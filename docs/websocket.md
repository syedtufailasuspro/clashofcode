# WebSocket Real-Time Battle Status (Django Channels)

This document explains the WebSocket setup used for opponent live status (typing, running, submit results) in the ClashOfCode battle arena. It includes architecture notes, the exact code snippets, setup steps, and common interview questions with short answers.

## What this solves

- Real-time opponent activity updates (Typing, Running, Submitted, TLE/MLE, etc.).
- Low-latency updates with a single WebSocket per player.
- Room-based broadcasting so both players see the same events.

## High-level flow

1. Browser opens a WebSocket to `/ws/battle/<battle_id>/`.
2. Django Channels routes this to `ChatConsumer`.
3. Consumer adds the socket to a room group (e.g., `battle_<battle_id>`).
4. Client sends `typing` or `action` messages.
5. Consumer broadcasts the message to the whole room group.
6. Each client updates the UI (Typing > Action > Thinking).

## Files involved

- `clashofcode/asgi.py`: ASGI entrypoint and protocol routing.
- `battle/routing.py`: WebSocket URL patterns.
- `battle/consumers.py`: WebSocket consumer with room broadcasting.
- `battle/static/battle/js/script.js`: Client WebSocket + status logic.
- `clashofcode/settings.py`: Channels + Redis configuration.

## Settings (Channels + Redis)

```python
# clashofcode/settings.py

INSTALLED_APPS = [
    "daphne",
    "channels",
    # ... other apps
]

ASGI_APPLICATION = "clashofcode.asgi.application"

# Example Redis channel layer on DB 1 (to avoid Celery DB 0)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": ["redis://127.0.0.1:6379/1"],
        },
    },
}
```

Why this matters:
- `channels` enables WebSocket support inside Django.
- `daphne` is the ASGI server used by Django dev server.
- `CHANNEL_LAYERS` tells Channels how to broadcast messages (Redis).

## ASGI routing

```python
# clashofcode/asgi.py

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clashofcode.settings")

django_asgi_app = get_asgi_application()

from battle.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
```

Why this matters:
- `ProtocolTypeRouter` sends HTTP traffic to Django, WS traffic to Channels.
- `AllowedHostsOriginValidator` blocks unexpected hosts.
- `AuthMiddlewareStack` adds user info to `scope` (optional but standard).

## WebSocket URL routing

```python
# battle/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/battle/(?P<room_name>[-\w]+)/$", consumers.ChatConsumer.as_asgi()),
]
```

Why this matters:
- `room_name` accepts UUIDs with hyphens.
- The URL matches the client WebSocket URL in JS.

## Consumer (room-based broadcast)

```python
# battle/consumers.py

import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"battle_{self.room_name}"

        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data):
        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            return

        payload_type = payload.get("type")
        if payload_type not in {"typing", "action"}:
            return

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "battle.message",
                "payload": payload,
            },
        )

    def battle_message(self, event):
        payload = event.get("payload", {})
        self.send(text_data=json.dumps(payload))
```

Why this matters:
- Each battle uses a room group (pub/sub channel).
- Every message goes to both players (including sender).
- `async_to_sync` is required because `WebsocketConsumer` is sync.

## Client WebSocket + status logic

```javascript
// battle/static/battle/js/script.js

const TYPING_THROTTLE_MS = 800;
const TYPING_TIMEOUT_MS = 2500;

const ACTION_LABELS = {
    RUNNING: "Running code",
    SUBMITTED: "Submitted code",
    FAILED_TC1: "Failed on test 1",
    TLE: "TLE",
    MLE: "MLE",
    WA: "Wrong answer",
    AC: "Accepted",
    RUN_COMPLETE: "Finished run"
};

let battleSocket = null;
let battleClientId = null;
let lastTypingSentAt = 0;
let opponentLastTypingAt = 0;
let opponentAction = "";
let opponentStatusEl = null;

function initRealtimeBattle() {
    const battleIdInput = document.getElementById("battleId");
    const roomNameEl = document.getElementById("room-name");
    const roomName = battleIdInput?.value || (roomNameEl ? JSON.parse(roomNameEl.textContent) : null);

    if (!roomName || !("WebSocket" in window)) {
        return;
    }

    opponentStatusEl = document.getElementById("opponentStatus");

    battleClientId = window.crypto && window.crypto.randomUUID
        ? window.crypto.randomUUID()
        : Math.random().toString(36).slice(2);

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socketUrl = `${protocol}://${window.location.host}/ws/battle/${roomName}/`;

    battleSocket = new WebSocket(socketUrl);

    battleSocket.onmessage = (event) => {
        let payload = null;
        try {
            payload = JSON.parse(event.data);
        } catch (error) {
            return;
        }

        if (payload.clientId && payload.clientId === battleClientId) {
            return;
        }

        if (payload.type === "typing") {
            opponentLastTypingAt = Date.now();
            renderOpponentStatus();
            return;
        }

        if (payload.type === "action") {
            opponentAction = payload.action || "";
            renderOpponentStatus();
        }
    };

    battleSocket.onclose = () => {
        battleSocket = null;
    };

    setInterval(renderOpponentStatus, 500);
}

function renderOpponentStatus() {
    if (!opponentStatusEl) {
        return;
    }

    const isTyping = Date.now() - opponentLastTypingAt <= TYPING_TIMEOUT_MS;

    if (isTyping) {
        opponentStatusEl.textContent = "Typing...";
        return;
    }

    if (opponentAction) {
        opponentStatusEl.textContent = ACTION_LABELS[opponentAction] || opponentAction;
        return;
    }

    opponentStatusEl.textContent = "Thinking";
}

function sendTypingPing() {
    if (!battleSocket || battleSocket.readyState !== WebSocket.OPEN) {
        return;
    }

    const now = Date.now();
    if (now - lastTypingSentAt < TYPING_THROTTLE_MS) {
        return;
    }

    lastTypingSentAt = now;
    battleSocket.send(JSON.stringify({
        type: "typing",
        clientId: battleClientId,
        ts: now
+    }));
+}
+
+function sendAction(action) {
+    if (!battleSocket || battleSocket.readyState !== WebSocket.OPEN) {
+        return;
+    }
+
+    battleSocket.send(JSON.stringify({
+        type: "action",
+        clientId: battleClientId,
+        action: action
     }));
 }
```

Why this matters:
- Typing pings are throttled to avoid spam.
- UI prioritizes Typing > Action > Thinking.
- `clientId` is used to ignore self messages.

## Recreate from scratch (step-by-step)

1. Install packages:
   - `pip install channels daphne channels_redis`
2. Add to `INSTALLED_APPS`:
   - `channels`, `daphne`
3. Configure `ASGI_APPLICATION` and `CHANNEL_LAYERS`.
4. Update `clashofcode/asgi.py` to include `ProtocolTypeRouter` and `URLRouter`.
5. Create `battle/routing.py` with the WebSocket URL.
6. Implement `ChatConsumer` with group add/send/discard.
7. Add battle page HTML:
   - A hidden input with `id="battleId"` and value `{{ battle.id }}`
   - A status element with `id="opponentStatus"`
8. Add `initRealtimeBattle()` to `script.js` and call it on DOM load.
9. Start Redis (Docker or local):
   - `docker run -p 6379:6379 redis`
10. Run server:
    - `python manage.py runserver`
11. Open two browsers on same battle room and test typing/status.

## Common interview questions (with short answers)

1. **Why use WebSockets instead of HTTP polling?**
   - WebSockets keep a single persistent connection, reduce overhead, and provide real-time low-latency updates.

2. **What is Channels and how does it integrate with Django?**
   - Channels extends Django to support async protocols (WebSocket). It uses an ASGI app and channel layers for message passing.

3. **Why do you need Redis here?**
   - The channel layer uses Redis to broadcast messages between connections and processes.

4. **What is the purpose of `group_add` and `group_send`?**
   - `group_add` subscribes a connection to a named room; `group_send` broadcasts to all connections in that room.

5. **Why `async_to_sync` in the consumer?**
   - `WebsocketConsumer` is synchronous; channel layer methods are async, so you must bridge them.

6. **How do you prevent message storms when typing?**
   - Use client-side throttling and short timeouts to reduce traffic.

7. **How do you handle multiple rooms?**
   - Use the room name in the URL and map it to a unique group name per battle.

8. **How do you secure WebSockets?**
   - Use `AllowedHostsOriginValidator`, auth middleware, and restrict to authenticated users if needed.

9. **What happens if Redis is down?**
   - Group sends fail, and clients won’t see each other’s events. The WS may still connect, but no broadcast happens.

10. **How would you scale this?**
    - Run multiple ASGI workers, keep Redis centralized, and ensure horizontal scaling behind a load balancer.

---

If you want, I can add a diagram of the message flow or a shorter interview-ready summary section.