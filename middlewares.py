from django.http import HttpResponseNotFound

class Force404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404:
            return HttpResponseNotFound("<h1>404 Not Found - Səhifə tapılmadı</h1>")
        return response
