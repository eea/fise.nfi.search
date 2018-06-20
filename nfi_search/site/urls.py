from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.documentation import include_docs_urls
from .spabundle import spabundle
from ..search import urls as search_urls

API_VERSION = '1'


urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'api/{API_VERSION}/search/', include(('nfi_search.search.urls', 'search'), namespace='search')),
    path(f'api/{API_VERSION}/docs', include_docs_urls(title='API Documentation', public=False)),
  ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        urlpatterns.append(
            path('__debug__/', include(debug_toolbar.urls))
        )


# Add the SPA catch-all route last
urlpatterns += [
    path('', spabundle, name='spa'),
]
