from rest_framework import routers
from .routers import main_routers


class DefaultRouter(routers.DefaultRouter):
    def extend(self, router):
        self.registry.extend(router.registry)


root = DefaultRouter()

for router in main_routers:
    root.extend(router)

urlpatterns = root.urls
