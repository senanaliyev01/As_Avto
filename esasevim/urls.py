from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'esasevim'

urlpatterns = [
    path('main/', views.esasevim, name='main'),
    path('get_statistics/', views.get_statistics, name='get_statistics'),
    path('rey_elave_et/', views.rey_elave_et, name='rey_elave_et'),
    path('yeni_mehsullar/', views.yeni_mehsullar, name='yeni_mehsullar'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

