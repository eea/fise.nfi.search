from rest_framework.serializers import ModelSerializer
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from .documents import DocumentDoc

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


class InfoLevelSerializer(ModelSerializer):
    class Meta:
        model = DInfoLevel
        fields = ('id', 'name')


class CountrySerializer(ModelSerializer):
    class Meta:
        model = DCountry
        fields = ('id', 'name')


class DataTypeSerializer(ModelSerializer):
    class Meta:
        model = DDataType
        fields = '__all__'


class DataSetSerializer(ModelSerializer):
    class Meta:
        model = DDataSet
        fields = '__all__'


class ResourceTypeSerializer(ModelSerializer):
    class Meta:
        model = DResourceType
        fields = '__all__'


class TopicCategorySerializer(ModelSerializer):
    class Meta:
        model = DTopicCategory
        fields = '__all__'


class NUTSLevelSerializer(ModelSerializer):
    class Meta:
        model = DNutsLevel
        fields = '__all__'


class KeywordSerializer(ModelSerializer):
    class Meta:
        model = DKeyword
        fields = '__all__'


class LanguageSerializer(ModelSerializer):
    class Meta:
        model = DLanguage
        fields = '__all__'


class DocumentDocSerializer(DocumentSerializer):
    class Meta:
        document = DocumentDoc
        fields = (
            'id',
            'description',
            'published_year',
            'data_collection_start_year',
            'data_collection_end_year',
            'next_update_year',
            'additional_info',
            'title',
            'country',
            'country_id',
            'data_type',
            'data_set',
            'resource_type',
            'info_level',
            'topic_category',
        )
