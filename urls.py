from django.urls import path
from . import views

urlpatterns = [
    path('get_current_rate/', views.get_current_rate, name='get_current_rate'),
] 