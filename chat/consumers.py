import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route'].get(
            'kwargs', {}).get('room_name')
        if self.room_name:
            self.room_group_name = f"chat_{self.room_name}"

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        username = text_data_json["username"]

        if message and hasattr(self, 'room_group_name'):
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "sendMessage",
                    "message": message,
                    "username": username,
                })

    async def sendMessage(self, event):
        # TODO handle save messages
        message = event["message"]
        username = event["username"]
        time_stamp = timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
        await self.send(text_data=json.dumps({"message": message, "username": username, "time_stamp": time_stamp}))
