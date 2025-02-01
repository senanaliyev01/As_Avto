from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.products_list, name='products_list'),
    path('sebet/ekle/<int:mehsul_id>/', views.sebet_ekle, name='sebet_ekle'),
    path('cart/', views.view_cart, name='view_cart'),
    path('sebet/sil/<int:sebet_id>/', views.sebetden_sil, name='sebetden_sil'),
    path('sifaris/gonder/', views.sifarisi_gonder, name='sifarisi_gonder'),
    path('orders/', views.sifaris_izle, name='sifaris_izle'),
    path('get_cart_count/', views.get_cart_count, name='get_cart_count'),
    path('orders_detail/<int:sifaris_id>/', views.sifaris_detallari, name='sifaris_detallari'),
    path('mehsul/<int:mehsul_id>/', views.mehsul_haqqinda, name='mehsul_haqqinda'),
    path('about/', views.about, name='about'),
    path('update_quantity/<int:item_id>/<int:new_quantity>/', views.update_quantity, name='update_quantity'),
    path('sifaris/<int:sifaris_id>/pdf/', views.generate_pdf, name='sifaris_pdf'),
    path('real-time-search/', views.real_time_search, name='real_time_search'),
]
