from django.urls import path
from . import views

urlpatterns = [
    path('', views.anaevim, name='anaevim'),  # Əsas səhifə
]
