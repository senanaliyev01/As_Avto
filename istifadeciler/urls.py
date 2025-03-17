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
    
    # Email təsdiqi və şifrə sıfırlama URL-ləri
    path('verify-email/', views.verify_email, name='verify_email'),
    path('resend-verification-email/', views.resend_verification_email, name='resend_verification_email'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('resend-reset-code/', views.resend_reset_code, name='resend_reset_code'),
]
