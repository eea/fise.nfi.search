from django.conf.urls import url
from .views import SearchView


urlpatterns = [
    url(r'^search/', SearchView.as_view({'get': 'list'}), name='search'),
]
