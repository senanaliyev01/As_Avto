from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin-as-avto-1983-2002/', admin.site.urls),
    path('istifadeciler/', include('istifadeciler.urls')),
    path('', include('anaevim.urls')),
    path('', include('esasevim.urls', namespace='esasevim')),
    path('', include('mehsullar.urls')),
    path('', include('rentacar.urls')),
    
    # Köhnə URL-ləri yeni URL-lərə yönləndir (301 Permanent Redirect)
    path('auth/register/', RedirectView.as_view(url='/istifadeciler/register/', permanent=True)),
    path('auth/login/', RedirectView.as_view(url='/istifadeciler/login/', permanent=True)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_title = 'AS-AVTO'
admin.site.site_header = 'Admin AS-AVTO'
admin.site.index_title = 'Admin Panel'

def custom_404_view(request, exception=None):
    return render(request, "404.html", status=404)

handler404 = custom_404_view
