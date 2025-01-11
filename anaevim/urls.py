from django.urls import path
from . import views

urlpatterns = [
    path('Ana Səhifə/', views.anaevim, name='anaevim'),  # Əsas səhifə
]
