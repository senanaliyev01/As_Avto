from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
import time
import logging

request_logger = logging.getLogger('django.request')

class Force404Middleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code == 404:
            return render(request, "404.html", status=404)
        return response

from mehsullar.models import Kateqoriya, Brend, Marka

class AddSearchDataMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Axtarış üçün lazım olan məlumatları əldə edin
        request.kateqoriyalar = Kateqoriya.objects.all()
        request.brendler = Brend.objects.all()
        request.markalar = Marka.objects.all()
        
class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            total_time = int((time.time() - request.start_time) * 1000)
            user = request.user.username if request.user.is_authenticated else 'AnonymousUser'
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
            
            # Request data-nı əldə et
            if request.method == 'GET':
                data = dict(request.GET.items())
            else:
                data = dict(request.POST.items())
            
            # Həssas məlumatları təmizlə
            if 'password' in data:
                data['password'] = '*****'
            if 'csrfmiddlewaretoken' in data:
                data['csrfmiddlewaretoken'] = '*****'
            
            log_data = {
                'ip': ip,
                'user': user,
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'time': total_time,
                'data': str(data)
            }

            # Status koduna görə log səviyyəsini təyin et
            if 200 <= response.status_code < 400:
                request_logger.info('Request completed successfully', extra=log_data)
            elif 400 <= response.status_code < 500:
                request_logger.warning('Client error occurred', extra=log_data)
            else:
                request_logger.error('Server error occurred', extra=log_data)

        return response

    def process_exception(self, request, exception):
        user = request.user.username if request.user.is_authenticated else 'AnonymousUser'
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        
        # Request data-nı əldə et
        if request.method == 'GET':
            data = dict(request.GET.items())
        else:
            data = dict(request.POST.items())
        
        # Həssas məlumatları təmizlə
        if 'password' in data:
            data['password'] = '*****'
        if 'csrfmiddlewaretoken' in data:
            data['csrfmiddlewaretoken'] = '*****'
        
        log_data = {
            'ip': ip,
            'user': user,
            'method': request.method,
            'path': request.path,
            'exc_info': str(exception),
            'data': str(data)
        }
        
        request_logger.error('Exception occurred', extra=log_data)
        
        