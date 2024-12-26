from django.urls import path
from . import views

urlpatterns = [
    path('main/', views.esasevim, name='main'),  # Əsas səhifə üçün yol
]
