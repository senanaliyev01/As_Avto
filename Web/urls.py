
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin-as-avto-1983-2002/', admin.site.urls),
    path('istifadeciler/', include('istifadeciler.urls')),
    path('', include('anaevim.urls')),
    path('', include('esasevim.urls')),
    path('', include('mehsullar.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

