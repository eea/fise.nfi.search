from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    OrderingFilterBackend,
    SearchFilterBackend,
)
from django_elasticsearch_dsl_drf.views import BaseDocumentViewSet

from .documents import DocumentDoc
from .serializers import DocumentDocSerializer


class SearchView(BaseDocumentViewSet):
    document = DocumentDoc
    serializer_class = DocumentDocSerializer
    lookup_field = 'id'
    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        SearchFilterBackend,
    ]
    search_fields = (
        'title',
        'country',
        'country_id',
        'data_type',
        'data_set',
        'resource_type',
        'info_level',
    )

    filter_fields = {
    }

