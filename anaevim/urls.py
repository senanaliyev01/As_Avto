from django.urls import path
from . import views

urlpatterns = [
    path('', views.anaevim, name='anaevim'),  # Əsas səhifə
    path('mehsul/<int:mehsul_id>/', views.mehsul_about, name='mehsul_about'),
]
