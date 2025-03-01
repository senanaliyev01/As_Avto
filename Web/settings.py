from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = os.environ.get('DEBUG')

ALLOWED_HOSTS = ['localhost','127.0.0.1','0.0.0.0', 'as-avto.com', 'www.as-avto.com']

CSRF_TRUSTED_ORIGINS = [
    'https://as-avto.com',
    'https://www.as-avto.com',
]

# SSL və HTTPS Təhlükəsizlik Tənzimləmələri
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS (HTTP Strict Transport Security) Tənzimləmələri
SECURE_HSTS_SECONDS = 31536000  # 1 il
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# SSL/TLS Təhlükəsizlik Başlıqları
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# SSL/TLS Version və Cipher Məhdudiyyətləri
SECURE_SSL_CIPHERS = (
    'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:'
    'ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305'
)

# TLS Version
SECURE_MIN_TLS_VERSION = 'TLSv1.3'

# SSL Session və Cookie Təhlükəsizliyi
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 31536000  # 1 il (365 gün)
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = True
CSRF_COOKIE_NAME = '__Secure-csrftoken'
CSRF_COOKIE_AGE = 86400  # 24 saat

# Əlavə Təhlükəsizlik Başlıqları
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# SSL Sertifikat Yenilənmə Tənzimləmələri
SECURE_SSL_REDIRECT_EXEMPT = []  # HTTPS yönləndirməsindən azad olan URL-lər
SECURE_REDIRECT_EXEMPT = []      # Ümumi yönləndirmədən azad olan URL-lər

# SSL/TLS Version Məhdudiyyətlərii
SECURE_SSL_CIPHERS = (
    'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:'
    'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:'
    'ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:'
    'DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384'
)

# Əlavə Təhlükəsizlik Tənzimləmələri
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_SSL_HOST = 'as-avto.com'  # SSL sertifikatının domain adı

# CORS Tənzimləmələri
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'https://as-avto.com',
    'https://www.as-avto.com',
]
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_EXPOSE_HEADERS = ['content-type', 'x-csrftoken']
CORS_ALLOW_CREDENTIALS = True

# DDoS Protection Settings
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/day',  # Anonim istifadəçilər üçün
        'user': '5000/day'  # Qeydiyyatlı istifadəçilər üçün
    }
}

# Application definition
INSTALLED_APPS = [
    # 'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'rest_framework',
    'anaevim',
    'istifadeciler',
    'mehsullar',
    'esasevim',
    'rentacar',
]

SITE_ID = 1

# Sitemap cache müddəti (6 saat = 21600 saniyə)
SITEMAP_CACHE_TIMEOUT = 21600

# 3. Jazzmin tənzimləmələri
# JAZZMIN_SETTINGS = {
#     # Başlıq
#     "site_title": "AS-AVTO",
#     "site_header": "İdarə Etmə",
#     "site_brand": "Admin",
#     "site_logo": "img/favicon.png",
#     "site_icon": "img/favicon.png",
#      "login_logo": "img/favicon.png",
    
#     # Admin panelin rəng sxemi
#     "theme": "default",
    
#     # Sidebar menyu
#     "show_sidebar": True,
#     "navigation_expanded": True,
    
#     # İstifadəçi interfeysi
#     "user_avatar": None,
    
#     # Top navbarda axtarış
#     "search_model": ["auth.User", "auth.Group"],
    
#     # Custom linklər
#     "custom_links": {
#         "books": [{
#             "name": "Statistika", 
#             "url": "make_messages", 
#             "icon": "fas fa-comments",
#         }]
#     },
    
#     # İkonlar
#     "icons": {
#         "auth": "fas fa-users-cog",
#         "auth.user": "fas fa-user",
#         "auth.Group": "fas fa-users",
#         "istifadeciler.Profile": "fas fa-user",
#         "mehsullar.Brend": "fas fa-industry icon",
#         "mehsullar.Kateqoriya": "fa-solid fa-list",
#         "mehsullar.Marka": "fa-solid fa-car",
#         "mehsullar.Mehsul": "fa-solid fa-boxes-stacked",
#         "mehsullar.MusteriReyi": "fa-solid fa-comment",
#         "mehsullar.Sebet": "fa-solid fa-cart-shopping",
#         "mehsullar.SifarisMehsul": "fa-solid fa-cart-plus",
#         "mehsullar.Sifaris": "fa-solid fa-bell",
#         "rentacar.CarImage": "fa-solid fa-car-side",
#         "rentacar.Car": "fa-solid fa-car",
#         "esasevim.HeroSlide": "fa-solid fa-house",
#     },
# }

# # 4. Admin interfeysi üçün əlavə tənzimləmələr
# JAZZMIN_UI_TWEAKS = {
#     "navbar_small_text": False,
#     "footer_small_text": False,
#     "body_small_text": False,
#     "brand_small_text": False,
#     "brand_colour": "navbar-success",
#     "accent": "accent-primary",
#     "navbar": "navbar-dark",
#     "no_navbar_border": False,
#     "sidebar": "sidebar-dark-primary",
#     "sidebar_nav_small_text": False,
#     "sidebar_disable_expand": False,
#     "sidebar_nav_child_indent": True,
#     "sidebar_nav_compact_style": False,
#     "sidebar_nav_legacy_style": False,
#     "sidebar_nav_flat_style": False,
# }

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'Web.middlewares.Force404Middleware',
    'Web.middlewares.AddSearchDataMiddleware',
    'Web.middlewares.RequestLoggingMiddleware',
    'Web.middlewares.SearchEnginePingMiddleware',
]

ROOT_URLCONF = 'Web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Web.wsgi.application'


#1123213232332 Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {

    'default': {

        'ENGINE': 'django.db.backends.postgresql_psycopg2',

        'NAME': os.getenv('POSTGRES_DB'),

        'USER': os.getenv('POSTGRES_USER'),

        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),

        'HOST': os.getenv('POSTGRES_HOST'),

        'PORT': os.getenv('POSTGRES_PORT'),

    }

}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'az'

TIME_ZONE = 'Asia/Baku'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


#11 Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logs qovluğunu yarat
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Logging konfiqurasiyası
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '{"timestamp":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s","path":"%(pathname)s","line":%(lineno)d}',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'verbose': {
            'format': '[{asctime}] [{levelname}] [{name}] [{pathname}:{lineno}] - {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '[{asctime}] [{levelname}] {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['require_debug_true'],
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'error.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'formatter': 'json',
            'encoding': 'utf-8',
        },
        'file_info': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'info.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'formatter': 'json',
            'encoding': 'utf-8',
        },
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'debug.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'formatter': 'verbose',
            'encoding': 'utf-8',
            'filters': ['require_debug_true'],
        },
        'file_request': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'requests.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'formatter': 'json',
            'encoding': 'utf-8',
        },
        'file_security': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'security.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 90,
            'formatter': 'json',
            'encoding': 'utf-8',
        },
        'file_performance': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'performance.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'formatter': 'json',
            'encoding': 'utf-8',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_info', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file_request', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['file_request'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file_security', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file_performance', 'file_error'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.template': {
            'handlers': ['file_debug'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'Web': {
            'handlers': ['console', 'file_info', 'file_error', 'file_debug'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'Web.security': {
            'handlers': ['file_security', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'Web.performance': {
            'handlers': ['file_performance'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}

# Session Tənzimləmələri
SESSION_COOKIE_AGE = 31536000  # 1 il (365 gün)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Browser bağlandıqda session silinməsin
SESSION_SAVE_EVERY_REQUEST = True  # Hər sorğuda session-u yenilə
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'

# Authentication Tənzimləmələri
LOGIN_URL = '/istifadeciler/login/'  # Login səhifəsinin URL-i
LOGIN_REDIRECT_URL = '/main/'  # Uğurlu giriş zamanı yönləndirilən səhifə
LOGOUT_REDIRECT_URL = '/istifadeciler/login/'  # Çıxış zamanı yönləndirilən səhifə

# Remember Me funksionallığı üçün
AUTH_USER_MODEL = 'auth.User'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
