from django.urls import path
from . import views

urlpatterns = [
    path('', views.anaevim, name='anaevim'),  # Əsas səhifə
    path('product/<int:mehsul_id>/<str:mehsul_adi>/<str:mehsul_brend_adi>/<str:mehsul_marka_adi>/<str:mehsul_brend_kod>/<str:mehsul_oem>/<str:mehsul_kateqoriya_adi>/', views.mehsul_etrafli, name='mehsul_etrafli'),  # Məhsul haqqında ətraflı
]
