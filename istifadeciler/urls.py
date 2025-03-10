from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('password-change/', views.password_change, name='password_change'),
    path('register/', views.register, name='register'),
    
    # Chat API
    path('api/chat/users/', views.get_chat_users, name='get_chat_users'),
    path('api/chat/messages/<int:receiver_id>/', views.get_messages, name='get_messages'),
    path('api/chat/send/', views.send_message, name='send_message'),
    path('api/chat/upload/', views.upload_file, name='upload_file'),
]
