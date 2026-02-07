# chat/consumers.py
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