from django.urls import path
from . import views

handler404 = 'home.views.custom_404'

urlpatterns = [
    path('', views.home_view, name='base'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('products/', views.products_view, name='products'),
    path('cart/', views.cart_view, name='cart'),
    path('orders/', views.orders_view, name='orders'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('load-more-products/', views.load_more_products, name='load_more_products'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('new-products/', views.new_products_view, name='new_products'),
]
