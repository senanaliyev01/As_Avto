import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from istifadeciler.models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        sender_id = text_data_json.get('sender')
        receiver_id = text_data_json.get('receiver')

        if message and sender_id and receiver_id:
            # Mesajı verilənlər bazasına yaz
            message_obj = await self.save_message(sender_id, receiver_id, message)
            
            # Mesajı göndərən və qəbul edən istifadəçilərə göndər
            await self.send(text_data=json.dumps({
                'message': {
                    'id': message_obj.id,
                    'content': message_obj.content,
                    'sender': message_obj.sender.username,
                    'is_mine': False,
                    'is_read': False,
                    'is_delivered': True
                }
            }))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        
        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=content,
            is_delivered=True
        )
        
        return message 