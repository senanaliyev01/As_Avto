from django.urls import path
from . import views

urlpatterns = [
    path('', views.anaevim, name='anaevim'),  # Əsas səhifə
    path('product/<int:mehsul_id>/', views.mehsul_etrafli, name='mehsul_etrafli_sade'),  # Sadə ID ilə
    path('product/<str:mehsul_adi>-<str:mehsul_oem>-<str:mehsul_brend_kod>/<int:mehsul_id>/', 
         views.mehsul_etrafli, 
         name='mehsul_etrafli'),  # Məhsul haqqında ətraflı
    path('catalogue/', views.catalogue, name='catalogue'),  # Kataloq səhifəsi
    path('catalogue/search/', views.catalogue_search, name='catalogue_search'),  # Kataloq axtarışı
]
