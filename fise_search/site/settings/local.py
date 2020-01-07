from .base import *

try:
    from debug_toolbar.settings import PANELS_DEFAULTS as DEFAULT_DEBUG_TOOLBAR_PANELS
except ImportError:
    DEFAULT_DEBUG_TOOLBAR_PANELS = []

INTERNAL_IPS = ['127.0.0.1', ]

INSTALLED_APPS += [
    'debug_toolbar',
    'elastic_panel',
]

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

DEBUG_TOOLBAR_PANELS = DEFAULT_DEBUG_TOOLBAR_PANELS + [
    'elastic_panel.panel.ElasticDebugPanel',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

CORS_ORIGIN_WHITELIST += [
    'localhost:8000',
]

# NFI_SEARCH_USE_TLS = False
# NFI_SEARCH_DOMAIN = 'localhost:8000'
