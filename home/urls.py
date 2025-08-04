from django.urls import path
from . import views
from .views import about_view, privacy_policy_view

handler404 = 'home.views.custom_404'

urlpatterns = [
    path('', views.root_view, name='root'),
    path('login/', views.login_view, name='login'),
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
    path('load-more-new-products/', views.load_more_new_products, name='load_more_new_products'),
    path('my-products/', views.my_products_view, name='my_products'),
    path('my-products/import/', views.import_user_products_view, name='import_user_products'),
    path('my-products/load-more/', views.load_more_my_products, name='load_more_my_products'),
    path('my-products/edit/<int:product_id>/', views.add_edit_product_view, name='edit_product_my'),
    path('my-products/delete/<int:product_id>/', views.delete_product_view, name='delete_product_my'),
    path('my-products/toggle-new/<int:product_id>/', views.toggle_product_new_status, name='toggle_product_new'),
    path('my-sales/', views.my_sales_view, name='my_sales'),
    path('my-sales/<int:order_id>/edit/', views.edit_my_sale_view, name='edit_my_sale'),
    path('my-sales/<int:order_id>/pdf/', views.my_sale_pdf, name='my_sale_pdf'),
    path('user-details/<int:user_id>/', views.user_details_view, name='user_details'),
    path('products/add/', views.add_edit_product_view, name='add_product'),
    path('products/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('products/<int:product_id>/edit/', views.add_edit_product_view, name='edit_product'),
    path('products/<int:product_id>/delete/', views.delete_product_view, name='delete_product'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('my-products/pdf/', views.my_products_pdf, name='my_products_pdf'),
    path('api/unread-sales-count/', views.unread_sales_count, name='unread_sales_count'),
    path('seller-admin-panel/', views.seller_admin_panel, name='seller_admin_panel'),
    path('my-products/change-image/<int:product_id>/', views.change_product_image, name='change_product_image'),
    path('like-product/', views.like_product, name='like_product'),
    path('rate-product/', views.rate_product, name='rate_product'),
    path('liked-products/', views.liked_products_view, name='liked_products'),
]

urlpatterns += [
    path('about/', about_view, name='about'),
    path('privacy-policy/', privacy_policy_view, name='privacy_policy'),
]
