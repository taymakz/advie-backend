import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# import sys
# sys.stdout.reconfigure(encoding='utf-8')

# Load the environment variables from the .env file
load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = os.environ.get('DEBUG') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',') if os.environ.get('ALLOWED_HOSTS') else []

# CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if os.environ.get(
#     'CORS_ALLOWED_ORIGINS') else []

CORS_ALLOW_ALL_ORIGINS = True

FRONTEND_URL = os.environ.get('FRONTEND_URL')
BACKEND_URL = os.environ.get('BACKEND_URL')

# Zarin Pal Config
ZARINPAL_MERCHANT = os.environ.get('ZARINPAL_MERCHANT')
ZARINPAL_SANDBOX = os.environ.get('ZARINPAL_SANDBOX') == 'True'

BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'storages',
    # Local Apps ------------------

    # API Section
    'site_api.api_configuration',

    # Settings Section
    'site_setting.website_management',
    'site_setting.website_banner',

    # Pages Section
    'site_pages.home_data',
    'site_pages.panel_data',

    # Users Section
    'site_account.user_management',
    'site_account.user_addresses',

    # Shop Section
    'site_shop.transaction_management',
    'site_shop.order_management',
    'site_shop.product_management',
    'site_shop.category_management',
    'site_shop.shipping_management',
    'site_shop.refund_management',
    'site_shop.coupon_management',

    # Notification Section
    'site_notification.verification_notification',
    'site_notification.user_notification',
    'site_notification.announcement_notification',

    # External Apps ------------------
    'django_filters',
    'mptt',
    'imagekit',
    'ckeditor',
    'ckeditor_uploader',
    'jalali_date'

]

AUTH_USER_MODEL = 'user_management.User'

DATABASES = {
    'default': {

    }
}
if os.getenv('DATABASE') == "LOCAL":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
elif os.getenv('DATABASE') == "POSTGRES":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DATABASE_NAME'),
            'USER': os.getenv('DATABASE_USER'),
            'PASSWORD': os.getenv('DATABASE_PASSWORD'),
            'HOST': os.getenv('DATABASE_HOST'),
            'PORT': os.getenv('DATABASE_PORT'),
        }
    }
elif os.getenv('DATABASE') == "POSTGRES_URL":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
        }
    }

if os.environ.get('STORAGE') == 'LOCAL':

    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'


elif os.environ.get('STORAGE') == 'SUPABASE':
    DEFAULT_FILE_STORAGE = 'django_storage_supabase.supabase'
    SUPABASE_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNrb3h3ZGdnZGFibWthdXhibHl4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY4NzcwMDI1NiwiZXhwIjoyMDAzMjc2MjU2fQ.0qsFiYhydh9q54_bA1aay894XBamKk0y4yQ7EbPVyFU'
    SUPABASE_URL = "https:ckoxwdggdabmkauxblyx"
    SUPABASE_ROOT_PATH = '/dir/'
    MEDIA_URL = f'{SUPABASE_URL}/media/'


elif os.environ.get('STORAGE') == 'LIARA':
    AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_URL = os.environ.get('AWS_URL')
    AWS_LOCATION = 'media'
    MEDIA_URL = f'{AWS_URL}/media/'

elif os.environ.get('STORAGE') == 'FTP':
    storage_host = os.environ.get('STORAGE_HOST')
    storage_port = os.environ.get('STORAGE_PORT')
    storage_user = os.environ.get('STORAGE_USER')
    storage_password = os.environ.get('STORAGE_PASSWORD')

    DEFAULT_FILE_STORAGE = 'storages.backends.ftp.FTPStorage'
    FTP_STORAGE_LOCATION = f'ftp://{storage_user}:{storage_password}@{storage_host}:{storage_port}/public_html/media'
    STORAGE_URL = os.environ.get('STORAGE_URL')
    MEDIA_URL = f'{STORAGE_URL}/media/'

STATIC_URL = '/static/'

if os.environ.get('WHITENOISE') == 'True':
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# CKEDITOR_UPLOAD_PATH = MEDIA_ROOT / 'contents'
CKEDITOR_UPLOAD_PATH = 'contents'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    "whitenoise.middleware.WhiteNoiseMiddleware",

    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
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

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = True

REST_FRAMEWORK = {

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication'
    ],
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'site_api.api_configuration.response.PaginationApiResponse',
    'PAGE_SIZE': 20
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=90),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",

    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

CELERY_BROKER_URL = "redis://localhost:6379/10"
CELERY_RESULT_BACKEND = "redis://localhost:6379/10"

# CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
# CELERY_RESULT_BACKEND = os.environ.get('CELERY_BROKER_URL')
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Tehran"
CELERY_ENABLE_UTC = False

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.c1.liara.email'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
