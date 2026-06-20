import os
from pathlib import Path
from decouple import config
import dj_database_url

SECRET_KEY = config("SECRET_KEY")
DEBUG = config('DEBUG', default=False, cast=bool)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent 

MPESA_CONSUMER_KEY = config('MPESA_CONSUMER_KEY')
MPESA_CONSUMER_SECRET = config('MPESA_CONSUMER_SECRET')
MPESA_SHORTCODE = config('MPESA_SHORTCODE')
MPESA_PASSKEY = config('MPESA_PASSKEY')
MPESA_CALLBACK_URL = config('MPESA_CALLBACK_URL')




# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG is loaded from environment to allow local development and production control.

ALLOWED_HOSTS = [
    ".onrender.com",
    "127.0.0.1",
    "localhost",
    "transcareagencies.co.ke",
    ".transcareagencies.co.ke",
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/products/'
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'products',
    'orders',
    'payments',
    'users',
    'jazzmin',
    'tailwind',
    'theme',
    'quotes',
    'cart',
    'pages',
    'accounts',
    'chatbot',
    'cloudinary',
    'cloudinary_storage',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.DashboardRedirectMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'orders.context_processors.cart_count',
                'core.context_processors.cart_counter',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASE_URL = config('DATABASE_URL', default='sqlite:///db.sqlite3')

DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
    )
}

if 'postgresql' in DATABASES['default'].get('ENGINE', ''):
    DATABASES['default'].setdefault('OPTIONS', {})
    DATABASES['default']['OPTIONS']['sslmode'] = 'require'

CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
    "https://transcareagencies.co.ke",
    "https://www.transcareagencies.co.ke",
    "https://shop.transcareagencies.co.ke",
]

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'users.User'

TAILWIND_APP_NAME = 'theme'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET'),
}

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")

PAYMENT_EMAIL = f"Trans Care Payments <{EMAIL_HOST_USER}>"
ORDERS_EMAIL = f"Trans Care Orders <{EMAIL_HOST_USER}>"
SECURITY_EMAIL = f"Trans Care Security Team <{EMAIL_HOST_USER}>"
SALES_EMAIL = f"Trans Care Sales Team <{EMAIL_HOST_USER}>"
SUPPORT_EMAIL = f"Trans Care Support <{EMAIL_HOST_USER}>"
RECEIPTS_EMAIL = f"Trans Care Receipts <{EMAIL_HOST_USER}>"

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

COMPANY_NAME = "Trans Care Agencies Ltd"

COMPANY_ADDRESS = "Eldoret, Kenya"

COMPANY_PO_BOX = "P.O Box 396-30100, Eldoret"

COMPANY_PHONE = "+254 713 147392"

COMPANY_EMAIL = "info.transcareagencies@gmail.com"

COMPANY_KRA_PIN = "P051234567A"

# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG

X_FRAME_OPTIONS = "DENY"

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'  # keep (safe)
MEDIA_ROOT = BASE_DIR / 'media'  # keep (safe)

STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

SECURE_PROXY_SSL_HEADER = (
    ('HTTP_X_FORWARDED_PROTO', 'https')
)

USE_X_FORWARDED_HOST = True