import json
import traceback
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from istifadeciler.models import Message
import logging

# Logging konfiqurasiyası
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            logger.info("WebSocket bağlantısı qurulur...")
            print("WebSocket bağlantısı qurulur...")
            
            # Otaq adını al (varsa)
            self.room_name = self.scope.get('url_route', {}).get('kwargs', {}).get('room_name', 'default')
            self.room_group_name = f'chat_{self.room_name}'
            
            logger.info(f"Otaq adı: {self.room_name}, Qrup adı: {self.room_group_name}")
            print(f"Otaq adı: {self.room_name}, Qrup adı: {self.room_group_name}")
            
            try:
                # Qrupa qoşul
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                
                # Bağlantını qəbul et
                await self.accept()
                logger.info("WebSocket bağlantısı qəbul edildi")
                print("WebSocket bağlantısı qəbul edildi")
                
                # Bağlantı uğurlu olduğunu bildir
                await self.send(text_data=json.dumps({
                    'status': 'connected',
                    'message': 'WebSocket bağlantısı uğurla quruldu'
                }))
            except Exception as e:
                logger.error(f"WebSocket bağlantısı qurularkən xəta: {str(e)}")
                print(f"WebSocket bağlantısı qurularkən xəta: {str(e)}")
                traceback.print_exc()
                
                # Xəta baş verdikdə də bağlantını qəbul et
                await self.accept()
                
                # Xəta mesajı göndər
                await self.send(text_data=json.dumps({
                    'status': 'error',
                    'message': f'WebSocket bağlantısı qurularkən xəta: {str(e)}'
                }))
        except Exception as e:
            logger.error(f"WebSocket bağlantısı qurularkən ümumi xəta: {str(e)}")
            print(f"WebSocket bağlantısı qurularkən ümumi xəta: {str(e)}")
            traceback.print_exc()
            
            # Xəta baş verdikdə də bağlantını qəbul et
            try:
                await self.accept()
                
                # Xəta mesajı göndər
                await self.send(text_data=json.dumps({
                    'status': 'error',
                    'message': f'WebSocket bağlantısı qurularkən ümumi xəta: {str(e)}'
                }))
            except Exception as inner_e:
                logger.error(f"Xəta mesajı göndərilərkən xəta: {str(inner_e)}")
                print(f"Xəta mesajı göndərilərkən xəta: {str(inner_e)}")
                traceback.print_exc()

    async def disconnect(self, close_code):
        try:
            logger.info(f"WebSocket bağlantısı bağlandı: {close_code}")
            print(f"WebSocket bağlantısı bağlandı: {close_code}")
            
            try:
                # Qrupdan çıx
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
            except Exception as e:
                logger.error(f"Qrupdan çıxarkən xəta: {str(e)}")
                print(f"Qrupdan çıxarkən xəta: {str(e)}")
                traceback.print_exc()
        except Exception as e:
            logger.error(f"WebSocket bağlantısı bağlanarkən ümumi xəta: {str(e)}")
            print(f"WebSocket bağlantısı bağlanarkən ümumi xəta: {str(e)}")
            traceback.print_exc()

    async def receive(self, text_data):
        try:
            logger.info(f"WebSocket mesajı alındı: {text_data}")
            print(f"WebSocket mesajı alındı: {text_data}")
            
            try:
                text_data_json = json.loads(text_data)
                message = text_data_json.get('message')
                sender_id = text_data_json.get('sender')
                receiver_id = text_data_json.get('receiver')

                print(f"Mesaj məlumatları: sender_id={sender_id}, receiver_id={receiver_id}, message={message}")

                if message and sender_id and receiver_id:
                    # Mesajı verilənlər bazasına yaz
                    message_obj = await self.save_message(sender_id, receiver_id, message)
                    
                    # Mesajı qrupa göndər
                    try:
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'chat_message',
                                'message': {
                                    'id': message_obj.id,
                                    'content': message_obj.content,
                                    'sender': message_obj.sender.username,
                                    'is_mine': False,
                                    'is_read': False,
                                    'is_delivered': True
                                }
                            }
                        )
                    except Exception as e:
                        logger.error(f"Mesaj qrupa göndərilərkən xəta: {str(e)}")
                        print(f"Mesaj qrupa göndərilərkən xəta: {str(e)}")
                        traceback.print_exc()
                    
                    # Mesajı göndərən və qəbul edən istifadəçilərə göndər
                    await self.send(text_data=json.dumps({
                        'message': {
                            'id': message_obj.id,
                            'content': message_obj.content,
                            'sender': message_obj.sender.username,
                            'is_mine': True,
                            'is_read': False,
                            'is_delivered': True
                        }
                    }))
                    print("Mesaj uğurla göndərildi")
                else:
                    print("Mesaj məlumatları tam deyil")
                    await self.send(text_data=json.dumps({
                        'error': 'Mesaj məlumatları tam deyil'
                    }))
            except Exception as e:
                logger.error(f"WebSocket mesajı işlənərkən xəta: {str(e)}")
                print(f"WebSocket mesajı işlənərkən xəta: {str(e)}")
                traceback.print_exc()
                await self.send(text_data=json.dumps({
                    'error': f'Xəta: {str(e)}'
                }))
        except Exception as e:
            logger.error(f"WebSocket mesajı alınarkən ümumi xəta: {str(e)}")
            print(f"WebSocket mesajı alınarkən ümumi xəta: {str(e)}")
            traceback.print_exc()
            
            try:
                await self.send(text_data=json.dumps({
                    'error': f'Ümumi xəta: {str(e)}'
                }))
            except Exception as inner_e:
                logger.error(f"Xəta mesajı göndərilərkən xəta: {str(inner_e)}")
                print(f"Xəta mesajı göndərilərkən xəta: {str(inner_e)}")
                traceback.print_exc()
    
    async def chat_message(self, event):
        """
        Qrupdan mesaj alındıqda bu funksiya çağırılır
        """
        try:
            message = event['message']
            
            # Mesajı müştəriyə göndər
            await self.send(text_data=json.dumps({
                'message': message
            }))
        except Exception as e:
            logger.error(f"Chat mesajı göndərilərkən xəta: {str(e)}")
            print(f"Chat mesajı göndərilərkən xəta: {str(e)}")
            traceback.print_exc()

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        try:
            sender = User.objects.get(id=sender_id)
            receiver = User.objects.get(id=receiver_id)
            
            message = Message.objects.create(
                sender=sender,
                receiver=receiver,
                content=content,
                is_delivered=True
            )
            
            return message
        except User.DoesNotExist:
            print(f"İstifadəçi tapılmadı: sender_id={sender_id}, receiver_id={receiver_id}")
            raise
        except Exception as e:
            print(f"Mesaj yadda saxlanarkən xəta: {str(e)}")
            traceback.print_exc()
            raise 