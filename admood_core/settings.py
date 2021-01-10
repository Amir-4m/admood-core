"""
Django settings for admood_core project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import ast
import os
from datetime import timedelta
from pathlib import Path

from celery.schedules import crontab
from decouple import config, Csv

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)
DEVEL = config("DEVEL", default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv())

SITE_URL = config("SITE_URL")
USER_VERIFICATION_URL = config("USER_VERIFICATION_URL", default='auth/register/verify')
USER_RESET_PASSWORD_URL = config("USER_RESET_PASSWORD_URL", default='auth/forget/verify')
LOGIN_URL = config("LOGIN_URI")

CORS_ORIGIN_ALLOW_ALL = True

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

AUTH_USER_MODEL = 'accounts.User'

USER_VERIFICATION_CODE_MIN_VALUE = config("USER_VERIFICATION_CODE_MIN_VALUE", default=100000)
USER_VERIFICATION_CODE_MAX_VALUE = config("USER_VERIFICATION_CODE_MAX_VALUE", default=999999)
USER_VERIFICATION_LIFETIME = config("USER_VERIFICATION_CODE_LIFETIME", default=2)

# Application definition
INSTALLED_APPS = [
    'apps.campaign.apps.CampaignConfig',
    'apps.core.apps.CoreConfig',
    'apps.accounts.apps.AccountsConfig',
    'apps.device.apps.DeviceConfig',
    'apps.medium.apps.MediumConfig',
    'apps.payments.apps.PaymentConfig',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'django_admin_json_editor',
    'django_json_widget'
]

if DEVEL:
    INSTALLED_APPS.append(
        'corsheaders'
    )

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEVEL:
    MIDDLEWARE.append(
        'corsheaders.middleware.CorsMiddleware',
    )

ROOT_URLCONF = 'admood_core.urls'
APPEND_SLASH = False

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
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

WSGI_APPLICATION = 'admood_core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config("DB_NAME"),
        'USER': config("DB_USER", default=''),
        'PASSWORD': config("DB_PASS", default=''),
        'HOST': config("DB_HOST", default='localhost'),
        'PORT': config("DB_PORT", default=''),
    }
}

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'JWT': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
}

CACHES = {
    'default': {
        'BACKEND': config("CACHE_BACKEND", default='django.core.cache.backends.locmem.LocMemCache'),
        'LOCATION': config("CACHE_HOST"),
        'KEY_PREFIX': 'ADMOODCORE',
    },
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
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
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M',
    'TIME_FORMAT': '%H:%M',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1/minute',
    }
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'apps.accounts.backends.EmailAuthBackend',
    'apps.accounts.backends.PhoneAuthBackend',
    # 'apps.accounts.backends.GoogleAuthBackend',
]

SIMPLE_JWT = {
    'ROTATE_REFRESH_TOKENS': True,
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('ACCESS_TOKEN_LIFETIME_MINUTES', default=30, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('REFRESH_TOKEN_LIFETIME_DAYS', default=90, cast=int)),
}

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
LANGUAGE_CODE = config("LANGUAGE_CODE", default="en-us")
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_L10N = False
USE_TZ = False
USE_THOUSAND_SEPARATOR = True
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_ROOT = BASE_DIR / 'static'
STATIC_URL = '/static/'

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# if DEVEL is False:
#     import sentry_sdk
#     from sentry_sdk.integrations.django import DjangoIntegration
#     from sentry_sdk.integrations.celery import CeleryIntegration
#
#     sentry_sdk.init(
#         dsn=f"https://{config('SENTRY_KEY')}@{config('SENTRY_HOST')}/{config('SENTRY_PROJECT_ID')}",
#         integrations=[
#             DjangoIntegration(),
#             CeleryIntegration()
#         ],
#
#         # If you wish to associate users to errors (assuming you are using
#         # django.contrib.auth) you may enable sending PII data.
#         send_default_pii=True,
#
#         # Custom settings
#         debug=True,
#         environment=config('SENTRY_ENV', default='development')  # 'production'
#     )

LOG_DIR = BASE_DIR / 'logs'
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS')

CELERY_BROKER_URL = config("CELERY_BROKER_URL")
CELERY_BROKER_USER = config("CELERY_BROKER_USER")
CELERY_BROKER_PASSWORD = config("CELERY_BROKER_PASSWORD")

CREATE_TELEGRAM_CAMPAIGN_TASK_CRONTAB = ast.literal_eval(config("CREATE_TELEGRAM_CAMPAIGN_TASK_CRONTAB"))
UPDATE_TELEGRAM_INFO_TASK_CRONTAB = ast.literal_eval(config('UPDATE_TELEGRAM_INFO_TASK_CRONTAB'))
UPDATE_TELEGRAM_PUBLISHERS_TASK_CRONTAB = ast.literal_eval(config('UPDATE_TELEGRAM_PUBLISHERS_TASK_CRONTAB'))

CELERY_BEAT_SCHEDULE = {
    "create_telegram_campaign_task": {
        "task": "apps.campaign.tasks.create_telegram_campaign_task",
        "schedule": crontab(**CREATE_TELEGRAM_CAMPAIGN_TASK_CRONTAB),
    },
    "update_telegram_info_task": {
        "task": "apps.campaign.tasks.update_telegram_info_task",
        "schedule": crontab(**UPDATE_TELEGRAM_INFO_TASK_CRONTAB),
    },
    "update_telegram_publishers_task": {
        "task": "apps.medium.tasks.update_telegram_publishers_task",
        "schedule": crontab(**UPDATE_TELEGRAM_PUBLISHERS_TASK_CRONTAB)
    },
    "create_instagram_campaign_task": {
        "task": "apps.campaign.tasks.create_instagram_campaign",
        "schedule": crontab(minute="*/1"),
    },
    "update_instagram_publishers_task": {
        "task": "apps.medium.tasks.update_instagram_publishers",
        "schedule": crontab(hour=0, minute=0)
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
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
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'verbose' if DEBUG else 'simple',
            'filename': LOG_DIR / 'django.log',
        },
        'db_queries': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'db_queries.log',
        },
    },
    'loggers': {
        'apps': {
            'level': 'DEBUG',
            'handlers': ['file', 'console'],
            'propagate': False
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['db_queries'],
            'propagate': False,
        }
    },
}

ADBOT_API_TOKEN = config("ADBOT_API_TOKEN")
ADBOT_API_URL = config('ADBOT_API_URL')
ADBOT_AGENTS = config('ADBOT_AGENTS', default='admood')
ADBOT_MAX_CONCURRENT_CAMPAIGN = config('ADBOT_MAX_CONCURRENT_CAMPAIGN', default=5, cast=int)

SMS_API_URL = config("SMS_API_URL")
SMS_API_TOKEN = config("SMS_API_TOKEN")

ADINSTA_API_URL = config('ADINSTA_API_URL')
ADINSTA_API_TOKEN = config("ADINSTA_API_TOKEN")

PAYMENT_API_URL = config('PAYMENT_API_URL', default='')
PAYMENT_SERVICE_SECRET = config('PAYMENT_SERVICE_SECRET', default='')

PAYMENT_REDIRECT_URL = config('PAYMENT_REDIRECT_URL', default='')
