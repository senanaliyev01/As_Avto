"""
ASGI config for Web project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django
import logging
import traceback

# Logging konfiqurasiyası
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("ASGI tətbiqi başladılır...")

try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Web.settings')
    django.setup()
    
    logger.info("Django quraşdırıldı")
    
    from django.core.asgi import get_asgi_application
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack
    from channels.security.websocket import AllowedHostsOriginValidator
    import Web.routing
    
    logger.info("ASGI modulları import edildi")
    
    # HTTP/HTTPS üçün standart ASGI tətbiqi
    http_application = get_asgi_application()
    logger.info("HTTP tətbiqi yaradıldı")
    
    # WebSocket və HTTP/HTTPS üçün ProtocolTypeRouter
    application = ProtocolTypeRouter({
        "http": http_application,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    Web.routing.websocket_urlpatterns
                )
            )
        ),
    })
    
    logger.info("ASGI tətbiqi konfiqurasiya edildi")
    print("ASGI tətbiqi konfiqurasiya edildi")
except Exception as e:
    logger.error(f"ASGI tətbiqi başladılarkən xəta: {str(e)}")
    print(f"ASGI tətbiqi başladılarkən xəta: {str(e)}")
    traceback.print_exc()
    
    # Xəta baş verdikdə sadəcə HTTP tətbiqini qaytarırıq
    try:
        from django.core.asgi import get_asgi_application
        application = get_asgi_application()
        logger.info("Xəta səbəbindən sadəcə HTTP tətbiqi yaradıldı")
    except Exception as e:
        logger.error(f"HTTP tətbiqi yaradılarkən xəta: {str(e)}")
        traceback.print_exc()
        raise
