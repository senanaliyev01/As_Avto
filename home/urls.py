from django.urls import path
from . import views

handler404 = 'home.views.custom_404'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('base/', views.home_view, name='base'),
    path('products/', views.products_view, name='products'),
    path('new-products/', views.new_products_view, name='new_products'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('orders/', views.orders_view, name='orders'),
    path('orders/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('logout/', views.logout_view, name='logout'),
    path('load-more-products/', views.load_more_products, name='load_more_products'),
    path('my-products/', views.my_products_view, name='my_products'),
    path('add-product/', views.add_product_view, name='add_product'),
    path('edit-product/<int:product_id>/', views.edit_product_view, name='edit_product'),
    path('incoming-orders/', views.incoming_orders_view, name='incoming_orders'),
    path('incoming-orders/<int:order_id>/', views.incoming_order_detail_view, name='incoming_order_detail'),
]
