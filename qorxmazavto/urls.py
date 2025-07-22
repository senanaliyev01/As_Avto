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




def robots_txt_view(request):
    with open('robots.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type="text/plain")



urlpatterns = [
    path('admin-as-avto-1983-2002/', admin.site.urls),
    path('', include('home.urls')),
    path('robots.txt', robots_txt_view),
    path('sitemap.xml', sitemap, {'sitemaps': {'products': ProductSitemap, 'static': StaticViewSitemap}, 'template_name': 'sitemap.xml'}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
