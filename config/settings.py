"""
Django settings for Optics Management System
"""
from pathlib import Path
import os

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = 'django-insecure-aq9+7!jqzsfn+ce++k23fk$6qgbp(t=jjypuag3xw&x@3pbvhg'
DEBUG = False
ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    "https://dhaioptics.com",
    "https://www.dhaioptics.com",
]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    "storages",
    
    # Local apps
    'customers',
    'sales',
    'stock',
    'employees',
    'reports',
    'settings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'config.context_processors.company_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'railway',
        'USER': 'postgres',
        'PASSWORD': 'yHnKunuNQdtFTmJsGtNmahFuPDsRigQP',
        'HOST': 'mainline.proxy.rlwy.net',
        'PORT': '38665',
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}



# Password validation
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
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_ROOT = BASE_DIR / 'media'





# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login settings
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Session settings (اختياري)
SESSION_COOKIE_AGE = 1209600  # أسبوعين
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # True في الإنتاج
SESSION_COOKIE_SAMESITE = 'Lax'
 
# Messages framework
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'info',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ==========================
# Supabase Storage (S3-Compatible)
# ==========================

# Supabase Project S3 values
AWS_ACCESS_KEY_ID = "8fb7c01269042adee2ce4485688909e7"
AWS_SECRET_ACCESS_KEY = "1bcf8d752643117480613a61d21b52173946622be7d0862a0fb4a9c9838fbc22"

AWS_STORAGE_BUCKET_NAME = "media"
AWS_S3_REGION_NAME = "ap-northeast-2"

# Supabase S3 endpoint — استخدمي الرابط الذي في لوحة Supabase
AWS_S3_ENDPOINT_URL = "https://xenkgkmzuinpgmswxajx.storage.supabase.co/storage/v1/s3"

# إعدادات S3 الضرورية لـ Supabase
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_ADDRESSING_STYLE = "path"
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False

# استخدمي التخزين عبر django-storages
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# رابط الوصول العام للملفات في bucket
MEDIA_URL = (
    "https://xenkgkmzuinpgmswxajx.storage.supabase.co/"
    "storage/v1/object/public/media/"
)
