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
    Document,
)


class InfoLevelSerializer(ModelSerializer):
    class Meta:
        model = DInfoLevel
        fields = ("id", "name")


class CountrySerializer(ModelSerializer):
    class Meta:
        model = DCountry
        fields = ("id", "name")


class DataTypeSerializer(ModelSerializer):
    class Meta:
        model = DDataType
        fields = "__all__"


class DataSetSerializer(ModelSerializer):
    class Meta:
        model = DDataSet
        fields = "__all__"


class ResourceTypeSerializer(ModelSerializer):
    class Meta:
        model = DResourceType
        fields = "__all__"


class TopicCategorySerializer(ModelSerializer):
    class Meta:
        model = DTopicCategory
        fields = "__all__"


class NUTSLevelSerializer(ModelSerializer):
    class Meta:
        model = DNutsLevel
        fields = "__all__"


class KeywordSerializer(ModelSerializer):
    class Meta:
        model = DKeyword
        fields = "__all__"


class LanguageSerializer(ModelSerializer):
    class Meta:
        model = DLanguage
        fields = "__all__"


class DocSerializer(ModelSerializer):
    download_url = SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            "id",
            "title",
            "download_url",
            "higher_level_docs",
            "same_level_docs",
            "lower_level_docs",
            "import_batch",
            "metadata_id",
        )

    @staticmethod
    def get_download_url(obj):
        if not obj.file or not obj.file.file:
            return None
        else:
            return obj.fq_download_url


class DocumentDocSerializer(DocumentSerializer):

    nuts_levels = SerializerMethodField()
    keywords = SerializerMethodField()
    download_url = SerializerMethodField()
    file_name = SerializerMethodField()
    file_size = SerializerMethodField()
    countries = SerializerMethodField()
    external_link = SerializerMethodField()
    organization_name = SerializerMethodField()
    organization_email = SerializerMethodField()

    class Meta:
        document = DocumentDoc
        fields = (
            "id",
            "title",
            "description",
            "country",
            "data_type",
            "data_set",
            "data_source",
            "resource_type",
            "info_level",
            "topic_category",
            "data_collection_start_year",
            "data_collection_end_year",
            "published_year",
            "next_update_year",
            "file_name",
            "file_size",
            "countries",
            "external_link",
            "organization_name",
            "organization_email",
            "higher_level_docs",
            "same_level_docs",
            "lower_level_docs",
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

    def get_download_url(self, obj):
        doc = self.Meta.document.Django.model.objects.get(pk=obj.id)
        if not doc.file or not doc.file.file:
            return None

        return doc.fq_download_url

    def get_file_name(self, obj):
        doc = self.Meta.document.Django.model.objects.get(pk=obj.id)
        if not doc.file or not doc.file.file:
            return None

        return doc.file.name

    def get_file_size(self, obj):
        doc = self.Meta.document.Django.model.objects.get(pk=obj.id)
        if not doc.file or not doc.file.file:
            return None

        return doc.file.size

    def get_countries(self, obj):
        doc = self.Meta.document.Django.model.objects.get(pk=obj.id)
        return sorted([c.name for c in doc.countries.all()])

    def get_external_link(self, obj):
        doc = self.Meta.document.Django.model.objects.get(pk=obj.id)
        if not doc.file or not doc.file.external_link:
            return None

        return doc.file.external_link

    def get_organization_name(self, obj):
        doc = self.Meta.document.Django.model.objects.get(pk=obj.id)
        if not doc.organization or not doc.organization.name:
            return None

        return doc.organization.name

    def get_organization_email(self, obj):
        doc = self.Meta.document.Django.model.objects.get(pk=obj.id)
        if not doc.organization or not doc.organization.email:
            return None

        return doc.organization.email
