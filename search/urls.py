
from django.conf.urls import url, include

from .views import hello_world


urlpatterns = [
    url(r'^demo/', hello_world, name='hello_world')]
