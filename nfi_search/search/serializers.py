from rest_framework.serializers import ModelSerializer, SerializerMethodField
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

    nuts_levels = SerializerMethodField()
    keywords = SerializerMethodField()

    class Meta:
        document = DocumentDoc
        fields = (
            'id',
            'title',
            'description',
            'country',
            'data_type',
            'data_set',
            'data_source',
            'resource_type',
            'info_level',
            'topic_category',
        )

    @staticmethod
    def get_nuts_levels(obj):
        if obj.nuts_levels:
            return [l.name for l in obj.nuts_levels]
        else:
            return []

    @staticmethod
    def get_keywords(obj):
        if obj.keywords:
            return [w.name for w in obj.keywords]
        else:
            return []
