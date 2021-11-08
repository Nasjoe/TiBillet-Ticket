"""
Django settings for TiBillet project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET')

# SECURITY WARNING: don't run with debug turned on in production!
# noinspection DjangoDebugModeSettings
if os.environ.get('DEBUG_DJANGO') == "True":
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition

SHARED_APPS = (
    'django_tenants',  # mandatory
    'jet.dashboard',
    'jet',
    'Customers', # you must list the app where your tenant model resides in

    'django.contrib.contenttypes',

    # everything below here is optional
    'django.contrib.auth',
    'AuthBillet',
    'QrcodeCashless',

    'rest_framework',
    'rest_framework.authtoken',
    'djoser',

    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'django_extensions',
    'Administration',
    'MetaBillet',

    'solo',
    'stdimage',

)

TENANT_APPS = (
    # The following Django contrib apps must be in TENANT_APPS
    'django.contrib.contenttypes',
    # your tenant-specific apps

    'BaseBillet',
    'ApiBillet',
    'PaiementStripe',

)

INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]
TENANT_MODEL = "Customers.Client" # app.Model
TENANT_DOMAIN_MODEL = "Customers.Domain"  # app.Model
ROOT_URLCONF = 'TiBillet.urls_tenants'
PUBLIC_SCHEMA_URLCONF = 'TiBillet.urls_public'
SITE_ID = 1
AUTH_USER_MODEL = 'AuthBillet.TibilletUser'


MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'TiBillet.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',  # Add 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

SIMPLE_JWT = {
   'AUTH_HEADER_TYPES': ('JWT',),
}

DJOSER = {
    "SEND_ACTIVATION_EMAIL": True,
    "PASSWORD_CHANGED_EMAIL_CONFIRMATION": True,
    "PASSWORD_RESET_CONFIRM_URL": "password/reset/confirm/{uid}/{token}",
    "USERNAME_RESET_CONFIRM_URL": "username/reset/confirm/{uid}/{token}",
    # "ACTIVATION_URL": "activate/{uid}/{token}",
    "ACTIVATION_URL": "user/activate/{uid}/{token}",
    # "SOCIAL_AUTH_ALLOWED_REDIRECT_URIS": ["http://manap.django-local.org:8002/"],
    'EMAIL': {
        'activation': 'AuthBillet.email.ActivationEmail',
        'confirmation': 'AuthBillet.email.ConfirmationEmail',
        'password_reset': 'AuthBillet.email.PasswordResetEmail',
        'password_changed_confirmation': 'AuthBillet.email.PasswordChangedConfirmationEmail',
        'username_changed_confirmation': 'AuthBillet.email.UsernameChangedConfirmationEmail',
        'username_reset': 'AuthBillet.email.UsernameResetEmail',
    },
}

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = os.environ.get('TIME_ZONE', 'UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "www", "static")
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, "www", "media")
MEDIA_URL = '/media/'

# EMAIL
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', False)
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', True)

# Celery Configuration Options
CELERY_TIMEZONE=os.environ.get('TIME_ZONE', 'UTC')
CELERY_TASK_TRACK_STARTED=True
CELERY_TASK_TIME_LIMIT=30 * 60
BROKER_URL=os.environ.get('CELERY_BROKER', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND=os.environ.get('CELERY_BACKEND', 'redis://redis:6379/0')
# DJANGO_CELERY_BEAT_TZ_AWARE=False


# Jet Menu
# -------------------------------------/

JET_SIDE_MENU_COMPACT = True
JET_CHANGE_FORM_SIBLING_LINKS = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        'logfile': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': f"{BASE_DIR}/www/Djangologfile",
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'logfile']
    },
}