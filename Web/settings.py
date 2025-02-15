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

ALLOWED_HOSTS = ['188.245.112.154','localhost','127.0.0.1','0.0.0.0', 'as-avto.com', 'www.as-avto.com']

CSRF_TRUSTED_ORIGINS = [
    'https://as-avto.com',
    'https://www.as-avto.com',
    'http://as-avto.com',
    'http://www.as-avto.com',
]

# SSL və HTTPS Təhlükəsizlik Tənzimləmələri
SECURE_SSL_REDIRECT = True  # HTTP -> HTTPS yönləndirmə
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True  # Session cookie-lər yalnız HTTPS üzərindən
CSRF_COOKIE_SECURE = True    # CSRF token-lər yalnız HTTPS üzərindən

# HSTS (HTTP Strict Transport Security) Tənzimləmələri
SECURE_HSTS_SECONDS = 31536000  # 1 il (saniyə ilə)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Bütün alt domainlər üçün HTTPS
SECURE_HSTS_PRELOAD = True  # HSTS preload siyahısına əlavə edir

# SSL/TLS Təhlükəsizlik Başlıqları
SECURE_BROWSER_XSS_FILTER = True  # XSS qoruması
SECURE_CONTENT_TYPE_NOSNIFF = True  # MIME type sniffing qoruması
X_FRAME_OPTIONS = 'DENY'  # Clickjacking qoruması

# Content Security Policy (CSP) Tənzimləmələri
CSP_DEFAULT_SRC = ("'self'", "https:", "data:", "ws:")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https:")
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'", "https:")
CSP_IMG_SRC = ("'self'", "https:", "data:", "blob:")
CSP_FONT_SRC = ("'self'", "https:", "data:")
CSP_CONNECT_SRC = ("'self'", "https:", "wss:")
CSP_FRAME_SRC = ("'self'", "https:")
CSP_MEDIA_SRC = ("'self'", "https:", "data:")
CSP_OBJECT_SRC = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_FORM_ACTION = ("'self'", "https:")
CSP_INCLUDE_NONCE_IN = ('script-src',)
CSP_REQUIRE_SRI_FOR = ('script', 'style')

# SSL Session və Cookie Təhlükəsizliyi
SESSION_COOKIE_HTTPONLY = True  # JavaScript-dən qorunma
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF hücumlarından qorunma
SESSION_COOKIE_AGE = 1209600  # 2 həftə
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Browser bağlandıqda session silinməsin

# CSRF Təhlükəsizliyi
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_AGE = 31536000  # 1 il
CSRF_USE_SESSIONS = True
CSRF_COOKIE_NAME = '__Secure-csrftoken'  # Secure prefix

# Əlavə Təhlükəsizlik Başlıqları
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
SECURE_BROWSER_XSS_FILTER = True

# SSL Sertifikat Yenilənmə Tənzimləmələri
SECURE_SSL_REDIRECT_EXEMPT = []  # HTTPS yönləndirməsindən azad olan URL-lər
SECURE_REDIRECT_EXEMPT = []      # Ümumi yönləndirmədən azad olan URL-lər

# SSL/TLS Version Məhdudiyyətləri
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
        'anon': '100/day',  # Anonim istifadəçilər üçün
        'user': '1000/day'  # Qeydiyyatlı istifadəçilər üçün
    }
}

# Application definition
INSTALLED_APPS = [
    'jazzmin',
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

# 3. Jazzmin tənzimləmələri
JAZZMIN_SETTINGS = {
    # Başlıq
    "site_title": "AS-AVTO",
    "site_header": "İdarə Etmə",
    "site_brand": "Admin",
    "site_logo": "img/favicon.png",
    "site_icon": "img/favicon.png",
     "login_logo": "img/favicon.png",
    
    # Admin panelin rəng sxemi
    "theme": "default",
    
    # Sidebar menyu
    "show_sidebar": True,
    "navigation_expanded": True,
    
    # İstifadəçi interfeysi
    "user_avatar": None,
    
    # Top navbarda axtarış
    "search_model": ["auth.User", "auth.Group"],
    
    # Custom linklər
    "custom_links": {
        "books": [{
            "name": "Statistika", 
            "url": "make_messages", 
            "icon": "fas fa-comments",
        }]
    },
    
    # İkonlar
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "istifadeciler.Profile": "fas fa-user",
        "mehsullar.Brend": "fas fa-industry icon",
        "mehsullar.Kateqoriya": "fa-solid fa-list",
        "mehsullar.Marka": "fa-solid fa-car",
        "mehsullar.Mehsul": "fa-solid fa-boxes-stacked",
        "mehsullar.MusteriReyi": "fa-solid fa-comment",
        "mehsullar.Sebet": "fa-solid fa-cart-shopping",
        "mehsullar.SifarisMehsul": "fa-solid fa-cart-plus",
        "mehsullar.Sifaris": "fa-solid fa-bell",
        "rentacar.CarImage": "fa-solid fa-car-side",
        "rentacar.Car": "fa-solid fa-car",
    },
}

# 4. Admin interfeysi üçün əlavə tənzimləmələr
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-success",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
}

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

# Logging konfiqurasiyası
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'request_format': {
            'format': '[{asctime}] [{levelname}] {message} - IP: {ip} - User: {user} - Method: {method} - Path: {path} - Status: {status} - Time: {time}ms - Data: {data}',
            'style': '{',
        },
        'error_format': {
            'format': '[{asctime}] [{levelname}] {message}\nException: {exc_info}\nPath: {path}\nMethod: {method}\nUser: {user}\nIP: {ip}\nData: {data}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'request_format',
        },
        'request_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/requests.log'),
            'formatter': 'request_format',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/errors.log'),
            'formatter': 'error_format',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['request_file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}
