from django.urls import path
from . import views

urlpatterns = [
    path('Məhsullar/', views.products_list, name='products_list'),
    path('sebet/ekle/<int:mehsul_id>/', views.sebet_ekle, name='sebet_ekle'),
    path('Səbət/', views.view_cart, name='view_cart'),
    path('sebet/sil/<int:sebet_id>/', views.sebetden_sil, name='sebetden_sil'),
    path('sifaris/gonder/', views.sifarisi_gonder, name='sifarisi_gonder'),
    path('Sifarişlərim/', views.sifaris_izle, name='sifaris_izle'),
    path('get_cart_count/', views.get_cart_count, name='get_cart_count'),
    path('orders_detail/<int:sifaris_id>/', views.sifaris_detallari, name='sifaris_detallari'),
   
    path('Məlumat/', views.about, name='about'),
    path('update_quantity/<int:item_id>/<int:new_quantity>/', views.update_quantity, name='update_quantity'),
    
]
