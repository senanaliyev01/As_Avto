from django.urls import path
from . import views

urlpatterns = [
    path('', views.anaevim, name='anaevim'),  # Əsas səhifə
    path('mehsul/<int:mehsul_id>/<slug:slug>/', views.mehsul_etrafli, name='mehsul_etrafli'),  # Məhsul haqqında ətraflı
]
