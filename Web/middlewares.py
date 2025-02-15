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

    def get_user_info(self, request):
        """İstifadəçi məlumatlarını əldə etmək üçün köməkçi funksiya"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            return {
                'username': request.user.username,
                'email': request.user.email,
                'id': request.user.id
            }
        
        # Session-dan istifadəçi məlumatlarını yoxla
        if request.session.get('_auth_user_id'):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(pk=request.session['_auth_user_id'])
                return {
                    'username': user.username,
                    'email': user.email,
                    'id': user.id
                }
            except User.DoesNotExist:
                pass
        
        return {'username': 'AnonymousUser', 'email': None, 'id': None}

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            total_time = int((time.time() - request.start_time) * 1000)
            
            # İstifadəçi məlumatlarını əldə et
            user_info = self.get_user_info(request)
            
            # IP ünvanını əldə et
            ip = request.META.get('HTTP_X_FORWARDED_FOR', '')
            if ip:
                ip = ip.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR', '')

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
            
            # Session məlumatlarını əlavə et (təhlükəsiz şəkildə)
            session_data = {}
            for key in request.session.keys():
                if 'password' not in key.lower() and 'token' not in key.lower():
                    session_data[key] = request.session[key]
            
            log_data = {
                'ip': ip,
                'user': user_info['username'],
                'user_id': user_info['id'],
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'time': total_time,
                'data': str(data),
                'session': str(session_data)
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
        user_info = self.get_user_info(request)
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        
        if request.method == 'GET':
            data = dict(request.GET.items())
        else:
            data = dict(request.POST.items())
        
        if 'password' in data:
            data['password'] = '*****'
        if 'csrfmiddlewaretoken' in data:
            data['csrfmiddlewaretoken'] = '*****'
        
        log_data = {
            'ip': ip,
            'user': user_info['username'],
            'user_id': user_info['id'],
            'method': request.method,
            'path': request.path,
            'exc_info': str(exception),
            'data': str(data)
        }
        
        request_logger.error('Exception occurred', extra=log_data)
        
        