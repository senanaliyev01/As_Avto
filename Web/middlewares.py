from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from mehsullar.models import Kateqoriya, Brend, Marka, Sebet
from django.db.models import Sum, F

class Force404Middleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code == 404:
            return render(request, "404.html", status=404)
        return response

class AddSearchDataMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Axtarış üçün lazım olan məlumatları əldə edin
        request.kateqoriyalar = Kateqoriya.objects.all()
        request.brendler = Brend.objects.all()
        request.markalar = Marka.objects.all()

class CartTotalMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            # İstifadəçinin səbətindəki cəmi məbləği hesablayır
            cart_total = Sebet.objects.filter(user=request.user).aggregate(total=Sum(F('miqdar') * F('mehsul__qiymet')))['total'] or 0
            request.cart_total = cart_total  # Cəmi məbləği request obyektinə əlavə et