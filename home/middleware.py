from .models import Sifaris, Kateqoriya, Firma, Avtomobil, Header_Message
from django.http import Http404
from django.conf import settings
from .views import custom_404
from django.shortcuts import render
from django.contrib.auth.models import User
from home.models import Mehsul

# class GlobalDataMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
# 
#     def __call__(self, request):
#         # Bütün aktiv mesajları əldə et
#         request.header_messages = Header_Message.objects.filter(aktiv=True).order_by('id')
# 
#         if request.user.is_authenticated:
#             # Ümumi borcu əldə edirik
#             statistics = Sifaris.get_order_statistics(request.user)
#             request.statistics = statistics
# 
#             # Axtarış üçün lazım olan məlumatları əldə edirik
#             request.categories = Kateqoriya.objects.all()
#             request.brands = Firma.objects.all()
#             request.models = Avtomobil.objects.all()
# 
#             # Bütün unikal satıcıları əlavə et
#             seller_ids = Mehsul.objects.exclude(sahib=None).values_list('sahib', flat=True).distinct()
#             sellers = list(User.objects.filter(id__in=seller_ids))
#             # AS-AVTO üçün pseudo-user əlavə et
#             class PseudoUser:
#                 def __init__(self, id, username):
#                     self.id = id
#                     self.username = username
#             sellers.insert(0, PseudoUser(0, 'AS-AVTO'))
#             request.sellers = sellers
# 
#         # Qlobal statistikalar (bütün səhifələr üçün)
#         request.total_user_count = User.objects.count()
#         request.total_seller_count = Mehsul.objects.exclude(sahib=None).values('sahib').distinct().count()
#         request.total_product_count = Mehsul.objects.count()
#         request.total_firma_count = Firma.objects.count()
# 
#         response = self.get_response(request)
#         return response 

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