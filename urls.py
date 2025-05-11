from django.urls import path
from . import views

urlpatterns = [
    path('sifarisler/', views.orders_view, name='orders'),
    path('sifaris/<int:order_id>/', views.order_detail_view, name='order_detail'),
] 