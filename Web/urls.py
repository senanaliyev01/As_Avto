from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.contrib.sitemaps.views import sitemap
from .sitemaps import sitemaps

urlpatterns = [
    path('admin-as-avto-1983-2002/', admin.site.urls),
    path('istifadeciler/', include('istifadeciler.urls')),
    path('', include('anaevim.urls')),
    path('', include('esasevim.urls', namespace='esasevim')),
    path('', include('mehsullar.urls')),
    path('', include('rentacar.urls')),
    
    # Sitemap URL - şəkil dəstəyi ilə
    path('sitemap.xml', sitemap, {
        'sitemaps': sitemaps,
        'template_name': 'sitemap_template.xml'
    }, name='django.contrib.sitemaps.views.sitemap'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_title = 'AS-AVTO'
admin.site.site_header = 'Admin AS-AVTO'
admin.site.index_title = 'Admin Panel'

def custom_404_view(request, exception=None):
    return render(request, "404.html", status=404)

handler404 = custom_404_view
