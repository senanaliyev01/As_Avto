"""
URL configuration for qorxmazavto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, FileResponse, Http404
from django.contrib.sitemaps.views import sitemap
from home.sitemaps import ProductSitemap, StaticViewSitemap
import os
from django.conf.urls.i18n import i18n_patterns




def robots_txt_view(request):
    with open('robots.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type="text/plain")

def service_worker_view(request):
    # Faylın tam yolunu göstər
    sw_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sw.js')
    if os.path.exists(sw_path):
        return FileResponse(open(sw_path, 'rb'), content_type='application/javascript')
    raise Http404("sw.js tapılmadı")

handler404 = 'home.views.custom_404'

urlpatterns = [
    path('admin-as-avto-1983-2002/', admin.site.urls),
    path('', include('home.urls')),
    path('robots.txt', robots_txt_view),
    path('sw.js', service_worker_view, name='service_worker'),
    path('sitemap.xml', sitemap, {'sitemaps': {'products': ProductSitemap, 'static': StaticViewSitemap}, 'template_name': 'sitemap.xml'}, name='django.contrib.sitemaps.views.sitemap'),
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
