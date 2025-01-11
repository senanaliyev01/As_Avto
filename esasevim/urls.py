from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('Əsas_Səhifə/', views.esasevim, name='main'),
    path('get_statistics/', views.get_statistics, name='get_statistics'),
    path('Rəy-əlavə-et/', views.rey_elave_et, name='rey_elave_et'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
