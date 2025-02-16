from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from mehsullar.models import Kateqoriya, Brend, Marka
from django.http import HttpResponseForbidden
import logging
import time
import json
import requests
from django.core.cache import cache
from datetime import datetime, timedelta

# Ayrı logger-lər yaradırıq
request_logger = logging.getLogger('django.request')
error_logger = logging.getLogger('django.security')
app_logger = logging.getLogger('Web')

class Force404Middleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code == 404:
            error_logger.warning(f"404 Error for path: {request.path}")
            return render(request, "404.html", status=404)
        return response

class AddSearchDataMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            # Axtarış üçün lazım olan məlumatları əldə edin
            request.kateqoriyalar = Kateqoriya.objects.all()
            request.brendler = Brend.objects.all()
            request.markalar = Marka.objects.all()
        except Exception as e:
            error_logger.error(f"AddSearchDataMiddleware error: {str(e)}", exc_info=True)

class RequestLoggingMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response
        self.SENSITIVE_FIELDS = {'password', 'csrfmiddlewaretoken', 'token', 'key', 'secret'}

    def _clean_data(self, data):
        cleaned = {}
        for key, value in data.items():
            if key in self.SENSITIVE_FIELDS:
                cleaned[key] = '*****'
            else:
                cleaned[key] = value
        return cleaned

    def process_request(self, request):
        request.start_time = time.time()
        
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            # Əsas məlumatları hazırla
            duration = int((time.time() - request.start_time) * 1000)
            user = request.user.username if request.user.is_authenticated else 'AnonymousUser'
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))

            # Request data
            request_data = {}
            if request.method == 'GET':
                request_data = self._clean_data(dict(request.GET.items()))
            elif request.method == 'POST':
                request_data = self._clean_data(dict(request.POST.items()))

            # Log məlumatlarını hazırla
            log_data = {
                'ip': ip,
                'user': user,
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'duration_ms': duration,
                'data': json.dumps(request_data),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'referer': request.META.get('HTTP_REFERER', '')
            }

            # Log səviyyəsini təyin et
            if 200 <= response.status_code < 400:
                request_logger.info(f"Request completed - {json.dumps(log_data)}")
            elif 400 <= response.status_code < 500:
                request_logger.warning(f"Client error - {json.dumps(log_data)}")
            else:
                error_logger.error(f"Server error - {json.dumps(log_data)}")

        return response

    def process_exception(self, request, exception):
        user = request.user.username if request.user.is_authenticated else 'AnonymousUser'
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        
        # Request data
        request_data = {}
        if request.method == 'GET':
            request_data = self._clean_data(dict(request.GET.items()))
        elif request.method == 'POST':
            request_data = self._clean_data(dict(request.POST.items()))

        # Exception məlumatlarını hazırla
        log_data = {
            'ip': ip,
            'user': user,
            'method': request.method,
            'path': request.path,
            'exception': str(exception),
            'data': json.dumps(request_data)
        }

        error_logger.error(
            f"Exception occurred - {json.dumps(log_data)}",
            exc_info=True
        )

class SearchEnginePingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Hər 24 saatda bir ping göndər
        last_ping = cache.get('last_search_engine_ping')
        now = datetime.now()
        
        if not last_ping or (now - last_ping) > timedelta(hours=24):
            try:
                # Google-a ping
                requests.get('https://www.google.com/ping?sitemap=https://as-avto.com/sitemap.xml')
                
                # Bing-ə ping
                requests.get('https://www.bing.com/ping?sitemap=https://as-avto.com/sitemap.xml')
                
                # Son ping vaxtını yadda saxla
                cache.set('last_search_engine_ping', now)
                
            except Exception as e:
                print(f"Search engine ping error: {str(e)}")
        
        