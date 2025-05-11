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