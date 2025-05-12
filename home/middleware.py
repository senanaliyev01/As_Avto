from django.conf import settings
from django.http import Http404
from django.template.loader import render_to_string
from django.http import HttpResponse
from .models import Sifaris, Kateqoriya, Firma, Avtomobil

class GlobalDataMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Ümumi borcu əldə edirik
            statistics = Sifaris.get_order_statistics(request.user)
            request.statistics = statistics

            # Axtarış üçün lazım olan məlumatları əldə edirik
            request.categories = Kateqoriya.objects.all()
            request.brands = Firma.objects.all()
            request.models = Avtomobil.objects.all()

        response = self.get_response(request)
        return response

class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if response.status_code == 404 and not settings.DEBUG:
            try:
                # 404.html səhifəsini render edirik
                html = render_to_string('404.html', {}, request)
                return HttpResponse(html, status=404)
            except:
                # Əgər 404.html tapılmazsa, sadə bir mesaj göstəririk
                return HttpResponse('Səhifə tapılmadı', status=404)
                
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, Http404) and not settings.DEBUG:
            try:
                html = render_to_string('404.html', {}, request)
                return HttpResponse(html, status=404)
            except:
                return HttpResponse('Səhifə tapılmadı', status=404)
        return None 