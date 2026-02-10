"""
Django settings for Chef Farah Ammar backend.
Production-ready; use environment variables for secrets.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'change-me-in-production')

DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'corsheaders',
    'accounts',
    'products',
    'orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# Use SQLite for local dev when DB_PASSWORD is not set (no PostgreSQL required)
if not os.environ.get('DB_PASSWORD') and os.environ.get('USE_POSTGRES', '') != '1':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'nanas_bites'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'OPTIONS': {'sslmode': 'prefer'} if not DEBUG else {},
        }
    }

AUTH_USER_MODEL = 'accounts.User'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework — production-ready: JWT + Token auth, rate limiting
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # tighten per-view as needed
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': os.environ.get('THROTTLE_ANON', '100/hour'),
        'user': os.environ.get('THROTTLE_USER', '200/hour'),
        'auth': os.environ.get('THROTTLE_AUTH', '10/hour'),  # login/register
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# CORS — allow React frontend
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
CORS_ALLOW_CREDENTIALS = True

# Payment (Stripe) — use env in production
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

# Checkout: tax and shipping (optional)
CHECKOUT_TAX_RATE = float(os.environ.get('CHECKOUT_TAX_RATE', '0'))  # e.g. 0.17 for 17%
CHECKOUT_SHIPPING_FIXED = float(os.environ.get('CHECKOUT_SHIPPING_FIXED', '0'))  # fixed shipping amount

# ---------- Security hardening ----------
# HTTPS: redirect HTTP to HTTPS in production (set behind a proxy that sets X-Forwarded-Proto)
SECURE_SSL_REDIRECT = not DEBUG and os.environ.get('SECURE_SSL_REDIRECT', '0') == '1'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # False so JS can read for API if needed; use SameSite
CSRF_COOKIE_SAMESITE = 'Lax'

# Password hashing: Django default PBKDF2 (strong); do not log or store plain passwords
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

# ---------- JWT (Simple JWT) — expiration + refresh tokens ----------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': __import__('datetime').timedelta(
        minutes=int(os.environ.get('JWT_ACCESS_MINUTES', '60')),
    ),
    'REFRESH_TOKEN_LIFETIME': __import__('datetime').timedelta(
        days=int(os.environ.get('JWT_REFRESH_DAYS', '7')),
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ---------- Logging: errors, access, and business events (orders, payments, stock) ----------
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_DIR = BASE_DIR / 'logs'
_log_handlers = ['console']
if not DEBUG and LOG_DIR.exists():
    _log_handlers.append('file')
if not DEBUG and os.environ.get('ADMINS'):
    _log_handlers.append('mail_admins')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': _log_handlers,
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django.request': {'level': 'WARNING'},
        'django.security': {'level': 'WARNING'},
        'orders': {'level': LOG_LEVEL},
        'products': {'level': LOG_LEVEL},
    },
}

# Admin email (critical errors). Format: "Name,email; Name2,email2"
_admins = os.environ.get('ADMINS', '')
if _admins:
    ADMINS = [tuple(a.strip().rsplit(',', 1)) for a in _admins.split(';') if ',' in a]
else:
    ADMINS = []

if not DEBUG:
    EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', '1') == '1'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'noreply@localhost')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', SERVER_EMAIL)

# ---------- Sentry (optional): set SENTRY_DSN to enable ----------
_sentry_dsn = os.environ.get('SENTRY_DSN', '')
if _sentry_dsn and not DEBUG:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    sentry_sdk.init(
        dsn=_sentry_dsn,
        environment=os.environ.get('SENTRY_ENVIRONMENT', 'production'),
        integrations=[
            DjangoIntegration(),
            LoggingIntegration(level=__import__('logging').INFO, event_level=__import__('logging').ERROR),
        ],
        traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
        send_default_pii=False,
    )
