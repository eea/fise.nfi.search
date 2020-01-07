from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.documentation import include_docs_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'api/', include(('fise_search.search.urls', 'fise-search'), namespace='search')),
    path(f'api-docs/', include_docs_urls(title='API Documentation', public=False)),
  ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    urlpatterns.append(
        path('api-browse/', include('rest_framework.urls'))
    )
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        urlpatterns.append(
            path('__debug__/', include(debug_toolbar.urls))
        )
