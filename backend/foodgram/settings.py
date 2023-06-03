import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    'DJANGO_TOKEN',
    default='django-insecure-x9$q82072np-88($=^j$a&9_t_1nthic)8)!g6m6=-4l@a!l90'
)

DEBUG = False

ALLOWED_HOSTS = ['*']

DATE_TIME_FORMAT = '%d/%m/%Y %H:%M'


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_filters',
    'api',
    'recipes',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram.urls'

TEMPLATES_DIR = BASE_DIR / 'templates'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
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

WSGI_APPLICATION = 'foodgram.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': os.getenv(
            'DB_ENGINE', default='django.db.backends.postgresql'
        ),
        'NAME': os.getenv(
            'DB_NAME', default='foodgram'
        ),
        'USER': os.getenv(
            'POSTGRES_USER', default='foodgram_user'
        ),
        'PASSWORD': os.getenv(
            'POSTGRES_PASSWORD', default='foodgram_password'
        ),
        'HOST': os.getenv(
            'DB_HOST', default='db'
        ),
        'PORT': os.getenv(
            'DB_PORT', default='5432'
        ),
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


LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = '/static_backend/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_backend')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

RECIPE_LIMIT_SUBSCRIBE = 25
DEFAULT_PAGE_PAGINATION = 25
MAX_PAGE_PAGINATION = 100
MIN_VALUE = 1
MAX_VALUE = 32000
ZERO = 0

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
}

DJOSER = {
    'SERIALIZERS': {
        'user_create': 'users.serializers.UserRegistrationSerializer',
        'user': 'users.serializers.UserSerializer',
        'current_user': 'users.serializers.UserSerializer',
    },
    'PERMISSIONS': {
        'user_list': ['rest_framework.permissions.AllowAny'],
        'user': ['djoser.permissions.CurrentUserOrAdminOrReadOnly']
    },
    'HIDE_USERS': False,
    'USER_ID_FIELD': 'id',
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
