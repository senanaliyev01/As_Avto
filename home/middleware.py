from .models import Sifaris, Kateqoriya, Firma, Avtomobil, Header_Message
from django.http import Http404
from django.conf import settings
from .views import custom_404
from django.shortcuts import render
from django.contrib.auth.models import User
from home.models import Mehsul

class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404 and settings.DEBUG:
            return custom_404(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, Http404) and settings.DEBUG:
            return custom_404(request)
        return None 