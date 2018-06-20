from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.documentation import include_docs_urls
from .spabundle import spabundle
from search import urls as api_urls


API_VERSION = '1'


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/%s/' % API_VERSION, include((api_urls, 'api'), namespace='api')),
    url(r'^api-docs/', include_docs_urls(title='API Documentation', public=False)),
  ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        urlpatterns.append(
            url(r'^__debug__/', include(debug_toolbar.urls))
        )


# Add the SPA catch-all route last
urlpatterns += [
    url(r'^', spabundle, name='spa'),
]
