
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
     path('jet/', include('jet.urls', 'jet')),
    path('admin-as-avto-1983-2002/', admin.site.urls),
    path('istifadeciler/', include('istifadeciler.urls')),
    path('', include('anaevim.urls')),
    path('', include('esasevim.urls')),
    path('', include('mehsullar.urls')),
    path('', include('rentacar.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_title = 'AS-AVTO'
admin.site.site_header = 'Admin AS-AVTO'
admin.site.index_title = 'Admin Panel'


from django.shortcuts import render

def custom_404_view(request, exception=None):
    return render(request, "404.html", status=404)

handler404 = custom_404_view
