from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-i*!f--&zqrna^p0iaz#+3lc9l2fg484wxkmzx+09#kizc5yv^p')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
if not DEBUG and 'RENDER_EXTERNAL_HOSTNAME' in os.environ:
    ALLOWED_HOSTS.append(os.environ['RENDER_EXTERNAL_HOSTNAME'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'cloudinary_storage',
    'cloudinary',

    'loja',
    'fabrica',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'penstore_backend.urls'

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

WSGI_APPLICATION = 'penstore_backend.wsgi.application'

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- NOVA CONFIGURAÇÃO CLOUDINARY USANDO COMPONENTES SEPARADOS ---
CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
API_KEY = os.environ.get('CLOUDINARY_API_KEY')
API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

if not DEBUG and CLOUD_NAME and API_KEY and API_SECRET:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': CLOUD_NAME,
        'API_KEY': API_KEY,
        'API_SECRET': API_SECRET,
    }
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
# --- FIM DA NOVA CONFIGURAÇÃO ---


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ORIGINS_ENV = os.environ.get('CORS_ORIGINS')
if CORS_ORIGINS_ENV:
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_ENV.split(',')]
else:
    CORS_ALLOWED_ORIGINS = []

if not DEBUG and 'RENDER_EXTERNAL_HOSTNAME' in os.environ:
    RENDER_HOST = os.environ['RENDER_EXTERNAL_HOSTNAME']
    CORS_ALLOWED_ORIGINS.append(f"http://{RENDER_HOST}")
    CORS_ALLOWED_ORIGINS.append(f"https://{RENDER_HOST}")

CORS_ALLOWED_ORIGINS.append("http://localhost:5173")
CORS_ALLOWED_ORIGINS.append("http://127.0.0.1:5173")


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication', 
        'rest_framework.authentication.SessionAuthentication', 
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated', 
    ]
}