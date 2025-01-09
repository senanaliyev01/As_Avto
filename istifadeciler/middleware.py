from django.utils import timezone
from django.contrib.auth.models import User
from django.core.cache import cache
from django.conf import settings

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # İstifadəçinin son aktivlik vaxtını cache-də saxla
            cache_key = f'user_{request.user.id}_last_seen'
            cache.set(cache_key, timezone.now(), settings.CACHE_TTL)
        return self.get_response(request) 