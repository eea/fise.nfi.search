import os
from getenv import env

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', 'secret')

SILENCED_SYSTEM_CHECKS = ["fields.W342"]
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', False)

ALLOWED_HOSTS = ['localhost', '127.0.0.1', env('ALLOWED_HOSTS')]

try:
    from debug_toolbar.settings import PANELS_DEFAULTS as DEFAULT_DEBUG_TOOLBAR_PANELS
except ImportError:
    DEFAULT_DEBUG_TOOLBAR_PANELS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_elasticsearch_dsl',
    'debug_toolbar',
    'elastic_panel',
    'webpack_loader',
    'rest_framework',
    'search',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

DEBUG_TOOLBAR_PANELS = DEFAULT_DEBUG_TOOLBAR_PANELS + [
    'elastic_panel.panel.ElasticDebugPanel',
]

ROOT_URLCONF = 'nfi_search.urls'

WSGI_APPLICATION = 'nfi_search.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': env('POSTGRES_HOST', 'postgres'),
        'NAME': env('POSTGRES_DBNAME', 'nfi'),
        'USER': env('POSTGRES_DBUSER', 'nfi'),
        'PASSWORD': env('POSTGRES_DBPASS', 'nfi'),
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}
# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

ROOT_DIR = BASE_DIR
STATIC_ROOT = os.path.join(ROOT_DIR, 'static')
STATIC_URL = '/static/'

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'webpack_bundles/',  # must end with slash
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': ['.+\.hot-update.js', '.+\.map']
    }
}

_WEBPACK_DIST_DIR = os.path.join(os.path.join(ROOT_DIR, 'frontend'), 'dist')

_WEBPACK_BUILD_DIR = os.path.join(_WEBPACK_DIST_DIR, 'build')
if os.path.isdir(_WEBPACK_BUILD_DIR):
    STATICFILES_DIRS = (
        _WEBPACK_BUILD_DIR,
    )

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
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


ELASTICSEARCH_DSL = {
    'default': {
        'hosts': env('ELASTICSEARCH_HOST'),
        'http_auth': env('ELASTICSEARCH_AUTH'),
        'timeout': env('ELASTICSEARCH_TIMEOUT', 10)
    },
}

MAX_RESULT_WINDOW = 10000  # This is ElasticSearch's default, but we define it
# here explicitly to minimize refactoring in case we ever change it.


# Imported files directory
FILES_DIR = env('FILES_PATH', required=True)

# Path of files to be imported
IMPORT_FILES_DIR = env('IMPORT_FILES_PATH')

# Root path of files in metadata
METADATA_FILES_DIR = env('METADATA_FILES_PATH')


TIKA_HOST = env('TIKA_HOST')
TIKA_PORT = env('TIKA_PORT', default=9998)
TIKA_URL = f'http://{TIKA_HOST}:{TIKA_PORT}'
TIKA_TIMEOUT = env('TIKA_TIMEOUT', 10)
