from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('password_change/', views.password_change, name='password_change'),
    path('logout/', views.logout_view, name='logout_view'),
    
    # Mesajlaşma URL-ləri
    path('chat/', views.chat_view, name='chat'),
    path('api/messages/unread-count/', views.get_unread_message_count, name='unread_message_count'),
    path('api/messages/chat-list/', views.get_chat_list, name='chat_list'),
    path('api/messages/<int:user_id>/', views.get_messages, name='get_messages'),
    path('api/messages/send/', views.send_message, name='send_message'),
    path('api/messages/mark-read/<int:message_id>/', views.mark_as_read, name='mark_as_read'),
    path('api/messages/delete/<int:message_id>/', views.delete_message, name='delete_message'),
]
