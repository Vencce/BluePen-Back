from pathlib import Path
import os
from datetime import timedelta
import environ # <--- NOVO: Importa a biblioteca de parsing

# Inicializa o django-environ
env = environ.Env(
    # Define valores padrao
    DEBUG=(bool, False),
    CLOUDINARY_URL=(str, ''),
    DATABASE_URL=(str, 'sqlite:///db.sqlite3')
)


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-i*!f--&zqrna^p0iaz#+3lc9l2fg484wxkmzx+09#kizc5yv^p')

# Lendo DEBUG via env
DEBUG = env('DEBUG') 

ALLOWED_HOSTS = [
    'bluepen.vercel.app', 
    'bluepan-back.onrender.com', 
    '.onrender.com', 
    '127.0.0.1' 
] 


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',
    'rest_framework.authtoken',
    
    'cloudinary_storage',
    'cloudinary',
    
    'loja',
    'fabrica',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'penstore_backend.wsgi.application'


# --- CONFIGURAÇÃO DE BANCO DE DADOS (LÊ DATABASE_URL) ---
DATABASES = {
    'default': env.db('DATABASE_URL')
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


# --- CONFIGURAÇÃO DE ARQUIVOS ESTÁTICOS E MÍDIA ---

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'

# LÊ A VARIAVEL CLOUDINARY_URL E CONFIGURA O ARMAZENAMENTO
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Adiciona a configuracao CLOUDINARY (necessaria para o SDK)
CLOUDINARY = {
    'CLOUDINARY_URL': env('CLOUDINARY_URL'),
    'SECURE': True
}


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CORS_ALLOWED_ORIGINS = [
    "https://bluepen.vercel.app",
    "http://localhost:5173", 
    "http://127.0.0.1:5173", 
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication', 
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}