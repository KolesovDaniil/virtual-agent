from pathlib import Path

import environ

env = environ.Env()
env.read_env('.env')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', str)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', bool, default=False)
CSRF_COOKIE_SECURE = not DEBUG
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS', list, default=[])

ALLOWED_HOSTS = env('ALLOWED_HOSTS', default=[])

AUTH_USER_MODEL = 'users.User'

BASE_URL = env('BASE_URL')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
    'chats.apps.ChatsConfig',
    'courses.apps.CoursesConfig',
    'faq.apps.FaqConfig',
    'materials.apps.MaterialsConfig',
    'notifications.apps.NotificationsConfig',
    'bot.apps.BotConfig',
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'virtual_agent.urls'

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
            ]
        },
    }
]

WSGI_APPLICATION = 'virtual_agent.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD', default=''),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env('POSTGRES_PORT', default=''),
    }
}

# REST Framework

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAdminUser'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'virtual_agent.exception_handlers.handle_bad_request',
    'DEFAULT_RENDERER_CLASSES': ('virtual_agent.renderer.EnvelopedJSONRenderer',),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'ASONIKA-K ADMIN',
    'DESCRIPTION': 'Your project description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

LATEST_API_VERSION = 1
API_PREFIX = 'api/'

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SECONDS = 1
MINUTES = 60 * SECONDS
HOURS = 60 * MINUTES
DAYS = 24 * HOURS
ABOUT_MONTH = 30 * DAYS
ABOUT_YEAR = 365 * DAYS
BYTES = 1
KiB = 1024 * BYTES
MiB = 1024 * KiB

MAX_FILE_SIZE_IN_BYTES = 20 * MiB


# MOODLE
MOODLE_BASE_URL = env('MOODLE_BASE_URL', str)
MOODLE_SUPERUSER_USERNAME = env('MOODLE_SUPERUSER_USERNAME', str)
MOODLE_SUPERUSER_PASSWORD = env('MOODLE_SUPERUSER_PASSWORD', str)
MOODLE_API_TIMEOUT_IN_SECONDS = 1

DEFAULT_FROM_EMAIL = 'agentped@yandex.ru'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_HOST_USER = env('SERVICE_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('SERVICE_EMAIL_HOST_PASSWORD')
EMAIL_PORT = 465
EMAIL_USE_SSL = True
