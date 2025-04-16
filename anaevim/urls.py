from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path

urlpatterns = [
    path('', views.anaevim, name='anaevim'),  # Əsas səhifə
    path('products-look-all-view/', views.mehsullar, name='mehsullar'),  # Məhsullar səhifəsi
    path('product/<int:mehsul_id>/', views.mehsul_etrafli, name='mehsul_etrafli_sade'),  # Sadə ID ilə
    path('product/<str:mehsul_adi>-<str:mehsul_oem>-<str:mehsul_brend_kod>/<int:mehsul_id>/', 
         views.mehsul_etrafli, 
         name='mehsul_etrafli'),  # Məhsul haqqında ətraflı
    path('gizlilik/', views.gizlilik, name='gizlilik'),
    path('realtime-search/', views.realtime_search, name='realtime_search'),
]
