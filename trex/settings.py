import os
from pathlib import Path

# Optional: load environment from a .env file when python-dotenv is available.
try:
    from dotenv import load_dotenv
    _DOTENV_AVAILABLE = True
except Exception:
    load_dotenv = lambda *a, **k: None
    _DOTENV_AVAILABLE = False

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env if python-dotenv is installed (optional)
if _DOTENV_AVAILABLE:
    load_dotenv(BASE_DIR / ".env")

# ===========================
# BASIC CONFIG (from .env)
# ===========================

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise Exception("SECRET_KEY no está definido en .env")

DEBUG = os.getenv("DEBUG", "True") == "True"

raw_hosts = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = raw_hosts.split(",") if raw_hosts else []

# ===========================
# APPLICATIONS
# ===========================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
    'rest_framework',
]

# ===========================
# MIDDLEWARE
# ===========================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ===========================
# URL & WSGI
# ===========================

ROOT_URLCONF = 'trex.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'trex.wsgi.application'

# ===========================
# DATABASE
# ===========================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST", "localhost"),
        'PORT': os.getenv("DB_PORT", "3306"),
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

# ===========================
# PASSWORDS
# ===========================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===========================
# INTERNATIONALIZATION
# ===========================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ===========================
# STATIC & MEDIA
# ===========================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# ===========================
# DJANGO REST FRAMEWORK
# ===========================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

# ===========================
# SECURITY (only when DEBUG=False)
# ===========================

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    X_FRAME_OPTIONS = 'DENY'
