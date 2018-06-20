from rest_framework import routers
from .routers import facets_router, search_router


class DefaultRouter(routers.DefaultRouter):
    def extend(self, router):
        self.registry.extend(router.registry)


root = DefaultRouter()
root.extend(facets_router)
root.extend(search_router)

urlpatterns = root.urls

