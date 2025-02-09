from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

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
        
        from django.utils.deprecation import MiddlewareMixin
from mehsullar.models import Sebet
from django.db.models import Sum, F

class AddCartTotalMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            sebet = Sebet.objects.filter(user=request.user)
            cemi_mebleg = sebet.aggregate(total=Sum(F('miqdar') * F('mehsul__qiymet')))['total'] or 0
            request.cemi_mebleg = cemi_mebleg
        else:
            request.cemi_mebleg = 0