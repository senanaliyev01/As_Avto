from django.urls import path
from . import views

urlpatterns = [
    path('Giriş/', views.login_view, name='login'),
    path('Qeydiyyat/', views.register, name='register'),
    path('Hesab/', views.profile, name='profile'),
    path('Şifrə Dəyişilməsi/', views.password_change, name='password_change'),
    path('Çıxış/', views.logout_view, name='logout'),
]
