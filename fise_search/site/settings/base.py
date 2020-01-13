import logging.config
from pathlib import Path
from getenv import env
from django.utils.log import DEFAULT_LOGGING


def split_env(var, sep=",", default="", required=False):
    value = env(var, default, required)
    return [e.strip() for e in value.split(sep) if e.strip()]


# <project>/fise_search
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Project dir
ROOT_DIR = BASE_DIR.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", "secret")

SILENCED_SYSTEM_CHECKS = ["fields.W342"]
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", False)

ALLOWED_HOSTS = ["localhost", "127.0.0.1", *split_env("ALLOWED_HOSTS")]

# Application definition

INSTALLED_APPS = [
    "fise_search.search.apps.Config",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "django_elasticsearch_dsl",
    "rest_framework",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = split_env("CORS_ORIGIN_WHITELIST")

ROOT_URLCONF = "fise_search.site.urls"

WSGI_APPLICATION = "fise_search.site.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": env("POSTGRES_HOST", "postgres"),
        "NAME": env("POSTGRES_DB", "nfi"),
        "USER": env("POSTGRES_USER", "nfi"),
        "PASSWORD": env("POSTGRES_PASSWORD", "nfi"),
        "PORT": env("POSTGRES_PORT", "5432"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}
# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_ROOT = ROOT_DIR / "static"
STATIC_URL = "/static/"

FIXTURE_DIRS = [ROOT_DIR / "data" / "fixtures"]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]


ELASTICSEARCH_DSL = {
    "default": {
        "hosts": env("ELASTICSEARCH_HOST"),
        "http_auth": env("ELASTICSEARCH_AUTH"),
        "timeout": env("ELASTICSEARCH_TIMEOUT", 10),
    }
}

ELASTICSEARCH_DSL_PARALLEL = True

ELASTICSEARCH_INDEX = env("ELASTICSEARCH_INDEX", "nfi")

# This is ElasticSearch's default, but we define it
# here explicitly to minimize refactoring in case we ever change it.
MAX_RESULT_WINDOW = 10000

# If this is True, multiple "keyword" filters will be OR'ed, otherwise they'll be AND'ed
KEYWORDS_DISJUNCTION = env("KEYWORDS_DISJUNCTION", True)

# Imported files directory
FILES_DIR = env("FILES_DIR", required=True)

# Path of files to be imported
IMPORT_FILES_DIR = env("IMPORT_FILES_DIR")

LOGGING_CONFIG = None
LOGLEVEL = env("LOGLEVEL", "info").upper()
ES_LOGLEVEL = env("ES_LOGLEVEL", "notset").upper()
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
            },
            "django.server": DEFAULT_LOGGING["formatters"]["django.server"],
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "console"},
            "django.server": DEFAULT_LOGGING["handlers"]["django.server"],
        },
        "loggers": {
            "": {"level": "WARNING", "handlers": ["console"]},
            "fise_search": {
                "level": LOGLEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "elasticsearch.trace": {
                "level": ES_LOGLEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "django.server": DEFAULT_LOGGING["loggers"]["django.server"],
        },
    }
)
