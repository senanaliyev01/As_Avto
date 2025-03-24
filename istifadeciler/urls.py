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
    path('check-code-expiration/', views.check_code_expiration, name='check_code_expiration'),
    path('check-code-approval/', views.check_code_approval, name='check_code_approval'),
    path('verify-login-code/', views.verify_login_code, name='verify_login_code'),
]
