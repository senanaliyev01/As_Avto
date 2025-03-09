from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('password_change/', views.password_change, name='password_change'),
    path('logout/', views.logout_view, name='logout_view'),
    
    # Chat URLs
    path('chat/', views.chat_box, name='chat_box'),
    path('chat/messages/<int:user_id>/', views.get_messages, name='get_messages'),
    path('chat/send/', views.send_message, name='send_message'),
    path('chat/unread/', views.get_unread_count, name='get_unread_count'),
]
