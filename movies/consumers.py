import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SeatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.theater_id = self.scope['url_route']['kwargs']['theater_id']
        self.room_group_name = f"seats_{self.theater_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def seat_update(self, event):
        await self.send(text_data=json.dumps({
            'seat_id': event['seat_id'],
            'is_booked': event['is_booked'],
        }))
