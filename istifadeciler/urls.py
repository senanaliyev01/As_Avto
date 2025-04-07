from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('password_change/', views.password_change, name='password_change'),
    path('logout/', views.logout_view, name='logout_view'),
    path('api/chat/users/', views.get_chat_users, name='get_chat_users'),
    path('api/chat/messages/<int:receiver_id>/', views.get_messages, name='get_messages'),
    path('api/chat/send/', views.send_message, name='send_message'),
    path('api/chat/group/messages/<int:group_id>/', views.get_group_messages, name='get_group_messages'),
    path('api/chat/group/send/', views.send_group_message, name='send_group_message'),
    path('check-code-expiration/', views.check_code_expiration, name='check_code_expiration'),
    path('check-code-approval/', views.check_code_approval, name='check_code_approval'),
    
    # Admin panel üçün
    path('admin/chat-group/<int:group_id>/members/', views.add_group_members, name='add_group_members'),
]
