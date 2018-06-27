from rest_framework.viewsets import ReadOnlyModelViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    IdsFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    SearchFilterBackend,
    FacetedSearchFilterBackend,
)
from django_elasticsearch_dsl_drf.pagination import PageNumberPagination
from django_elasticsearch_dsl_drf.views import BaseDocumentViewSet

from .documents import DocumentDoc
from .serializers import (
    InfoLevelSerializer,
    CountrySerializer,
    DataSetSerializer,
    DataTypeSerializer,
    ResourceTypeSerializer,
    TopicCategorySerializer,
    DocumentDocSerializer,
    NUTSLevelSerializer,
    KeywordSerializer,
    LanguageSerializer,
)

from .models import (
    DInfoLevel,
    DCountry,
    DDataType,
    DDataSet,
    DResourceType,
    DTopicCategory,
    DNutsLevel,
    DKeyword,
    DLanguage,
)


# Facets viewsets


class InfoLevelViewSet(ReadOnlyModelViewSet):
    queryset = DInfoLevel.objects.all()
    serializer_class = InfoLevelSerializer
    pagination_class = None


class CountryViewSet(ReadOnlyModelViewSet):
    queryset = DCountry.objects.all()
    serializer_class = CountrySerializer
    pagination_class = None


class DataTypeViewSet(ReadOnlyModelViewSet):
    queryset = DDataType.objects.all()
    serializer_class = DataTypeSerializer
    pagination_class = None


class DataSetViewSet(ReadOnlyModelViewSet):
    queryset = DDataSet.objects.all()
    serializer_class = DataSetSerializer
    pagination_class = None


class ResourceTypeViewSet(ReadOnlyModelViewSet):
    queryset = DResourceType.objects.all()
    serializer_class = ResourceTypeSerializer
    pagination_class = None


class TopicCategoryViewSet(ReadOnlyModelViewSet):
    queryset = DTopicCategory.objects.all()
    serializer_class = TopicCategorySerializer
    pagination_class = None


class NUTSLevelViewSet(ReadOnlyModelViewSet):
    queryset = DNutsLevel.objects.all()
    serializer_class = NUTSLevelSerializer
    pagination_class = None


class KeywordViewSet(ReadOnlyModelViewSet):
    queryset = DKeyword.objects.all()
    serializer_class = KeywordSerializer
    pagination_class = None


class LanguageViewSet(ReadOnlyModelViewSet):
    queryset = DLanguage.objects.all()
    serializer_class = LanguageSerializer
    pagination_class = None


class SearchPageNumberPagination(PageNumberPagination):
    """
    Pagination class for the search viewset. Accepts custom page sizes in
    URL params, and trims the verbose facets structure returned by
    `django_elasticsearch_dsl_drf.PageNumberPagination.get_facets`.
    """

    page_size_query_param = 'page_size'

    def get_facets(self, page=None):
        raw_facets = super().get_facets(page)
        if raw_facets is not None:
            facets = {}
            for filter_key, data in raw_facets.items():
                field = filter_key[8:]  # remove '_filter_' prefix
                facets[field] = {
                    b['key']: b['doc_count'] for b in data[field]['buckets']
                }
            return facets


class SearchViewSet(BaseDocumentViewSet):
    document = DocumentDoc
    serializer_class = DocumentDocSerializer
    pagination_class = SearchPageNumberPagination
    lookup_field = 'id'
    filter_backends = [
        FilteringFilterBackend,
        IdsFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
        FacetedSearchFilterBackend,
    ]
    search_fields = (
        'title',
        'description',
        # 'text',
    )
    _facets = (
        'country',
        'data_type',
        'data_set',
        'data_source',
        'info_level',
        'topic_category',
        'resource_type',
    )
    filter_fields = {f: f for f in _facets}
    faceted_search_fields = {
        field: {'field': field, 'enabled': True} for field in _facets
    }
    ordering_fields = {f: f for f in _facets}
    ordering = ('title',)
