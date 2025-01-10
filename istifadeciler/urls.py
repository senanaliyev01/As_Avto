from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('password-change/', views.password_change, name='password_change'),
    path('logout/', views.logout_view, name='logout'),
    path('messages/<int:receiver_id>/', views.get_messages, name='get_messages'),
    path('send-message/', views.send_message, name='send_message'),
    path('chat-users/', views.get_chat_users, name='get_chat_users'),
]