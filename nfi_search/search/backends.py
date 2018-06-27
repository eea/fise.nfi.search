from django_elasticsearch_dsl_drf.filter_backends.mixins import (
    FilterBackendMixin,
)
from rest_framework.filters import BaseFilterBackend

__all__ = ('NestedFacetedSearchFilterBackend',)


class NestedFacetedSearchFilterBackend(BaseFilterBackend, FilterBackendMixin):
    """
    Adds nesting to keywords and NUTS levels.

    Implemented as workaround until issue

        https://github.com/barseghyanartur/django-elasticsearch-dsl-drf/issues/52

    is resolved.

    There is no toggling of facets using query params, the facets are always on.
    """

    def filter_queryset(self, request, queryset, view):
        queryset.aggs \
            .bucket('_filter_nuts_level',
                    'nested',
                    path='nuts_levels') \
            .bucket('nuts_level',
                    'terms',
                    field='nuts_levels.name')

        queryset.aggs \
            .bucket('_filter_keyword',
                    'nested',
                    path='keywords') \
            .bucket('keyword',
                    'terms',
                    field='keywords.name')

        return queryset
