"""
Django settings for CAI - Centro Aquetico Infatil
C.A.I — Versão com Segurança Reforçada
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-cai-CHANGE-THIS-IN-PRODUCTION-use-env-var-always'
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
USE_JAZZMIN = os.environ.get('USE_JAZZMIN', 'False') == 'True'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'apps.accounts',
    'apps.alunos',
    'apps.professores',
    'apps.turmas',
    'apps.financeiro',
    'apps.dashboard',
]

if USE_JAZZMIN:
    INSTALLED_APPS.insert(0, 'jazzmin')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.accounts.middleware.SecurityHeadersMiddleware',
    'apps.accounts.middleware.LoginRateLimitMiddleware',
]

ROOT_URLCONF = 'cai_system.urls'

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

WSGI_APPLICATION = 'cai_system.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'accounts.Usuario'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Recife'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 8 * 60 * 60
SESSION_SAVE_EVERY_REQUEST = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_FAILURE_VIEW = 'apps.accounts.views.csrf_failure'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {'anon': '20/hour', 'user': '500/hour'},
}

if USE_JAZZMIN:
    JAZZMIN_SETTINGS = {
        "site_title": "CAI Admin",
        "site_header": "Centro Aquetico Infatil",
        "site_brand": "C.A.I",
        "welcome_sign": "Bem-vindo ao Painel Administrativo",
        "copyright": "C.A.I",
        "search_model": ["accounts.Usuario", "alunos.Aluno"],
        "topmenu_links": [{"name": "Portal", "url": "/", "permissions": ["auth.view_user"]}],
        "show_sidebar": True,
        "navigation_expanded": True,
        "icons": {
            "accounts.Usuario": "fas fa-users-cog",
            "alunos.Aluno": "fas fa-child",
            "alunos.Responsavel": "fas fa-user-friends",
            "professores.Professor": "fas fa-chalkboard-teacher",
            "turmas.Turma": "fas fa-swimming-pool",
            "turmas.Matricula": "fas fa-id-card",
            "financeiro.Mensalidade": "fas fa-money-bill-wave",
            "financeiro.Pagamento": "fas fa-receipt",
        },
        "default_icon_parents": "fas fa-chevron-circle-right",
        "default_icon_children": "fas fa-circle",
        "related_modal_active": True,
        "show_ui_builder": False,
    }
    JAZZMIN_UI_TWEAKS = {
        "sidebar_fixed": True,
        "sidebar": "sidebar-dark-primary",
        "navbar": "navbar-white navbar-light",
        "brand_colour": "navbar-primary",
        "accent": "accent-primary",
        "theme": "default",
    }

import os as _os
_os.makedirs(BASE_DIR / 'logs', exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{levelname} {asctime} {module} {message}', 'style': '{'},
    },
    'handlers': {
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': str(BASE_DIR / 'logs' / 'security.log'),
            'formatter': 'verbose',
        },
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
    },
    'loggers': {
        'django.security': {'handlers': ['security_file', 'console'], 'level': 'WARNING', 'propagate': False},
        'apps.accounts': {'handlers': ['security_file', 'console'], 'level': 'INFO', 'propagate': False},
    },
}
