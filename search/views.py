from django.views.generic import ListView
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    OrderingFilterBackend,
    SearchFilterBackend,
)
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


class InfoLevelViewSet(ReadOnlyModelViewSet):
    queryset = DInfoLevel.objects.all()
    serializer_class = InfoLevelSerializer


class CountryViewSet(ReadOnlyModelViewSet):
    queryset = DCountry.objects.all()
    serializer_class = CountrySerializer


class DataTypeViewSet(ReadOnlyModelViewSet):
    queryset = DDataType.objects.all()
    serializer_class = DataTypeSerializer


class DataSetViewSet(ReadOnlyModelViewSet):
    queryset = DDataSet.objects.all()
    serializer_class = DataSetSerializer


class ResourceTypeViewSet(ReadOnlyModelViewSet):
    queryset = DResourceType.objects.all()
    serializer_class = ResourceTypeSerializer


class TopicCategoryViewSet(ReadOnlyModelViewSet):
    queryset = DTopicCategory.objects.all()
    serializer_class = TopicCategorySerializer


class NUTSLevelViewSet(ReadOnlyModelViewSet):
    queryset = DNutsLevel.objects.all()
    serializer_class = NUTSLevelSerializer


class KeywordViewSet(ReadOnlyModelViewSet):
    queryset = DKeyword.objects.all()
    serializer_class = KeywordSerializer


class LanguageViewSet(ReadOnlyModelViewSet):
    queryset = DLanguage.objects.all()
    serializer_class = LanguageSerializer


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

