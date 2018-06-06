from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from .documents import DocumentDoc


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
