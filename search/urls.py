from rest_framework import routers
from .routers import facets_router


class DefaultRouter(routers.DefaultRouter):
    def extend(self, router):
        self.registry.extend(router.registry)


root = DefaultRouter()
root.extend(facets_router)

urlpatterns = root.urls

