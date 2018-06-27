from django.conf import settings
from django_elasticsearch_dsl import DocType, Index, fields
from elasticsearch_dsl.analysis import analyzer, normalizer, char_filter
from .models import Document


nfi = Index('nfi')
nfi.settings(max_result_window=settings.MAX_RESULT_WINDOW)

lowercase_normalizer = normalizer(
    type='custom',
    name_or_instance='lowercase_normalizer',
    char_filter=[],
    filter='lowercase',
)

no_digits_char_filter = char_filter(
    name_or_instance='no_digits',
    type='pattern_replace',
    pattern='(\\d+)',
    replace=''
)

no_digits_analyzer = analyzer(
    name_or_instance='no_digits',
    tokenizer='standard',
    filter=['standard', 'lowercase', 'stop'],
    char_filter=[no_digits_char_filter]
)


@nfi.doc_type
class DocumentDoc(DocType):

    title = fields.TextField(
        analyzer='standard',
        boost=5.0,
        fielddata=True,
    )

    description = fields.TextField(
        analyzer='standard',
        boost=2.0,
        fielddata=True,
    )

    text = fields.TextField(
        analyzer=no_digits_analyzer,
        fielddata=True,
    )

    country = fields.KeywordField(
        attr='country.name',
        normalizer=lowercase_normalizer
    )

    data_type = fields.KeywordField(
        attr='data_type.name',
        normalizer=lowercase_normalizer
    )

    data_set = fields.KeywordField(
        attr='data_set.name',
        normalizer=lowercase_normalizer
    )

    data_source = fields.KeywordField(
        attr='data_source.name',
        normalizer=lowercase_normalizer
    )

    info_level = fields.KeywordField(
        attr='info_level.name',
        normalizer=lowercase_normalizer
    )

    resource_type = fields.KeywordField(
        attr='resource_type.name',
        normalizer=lowercase_normalizer
    )

    topic_category = fields.KeywordField(
        attr='topic_category.name',
        normalizer=lowercase_normalizer
    )

    keywords = fields.NestedField(
        properties={
            'name': fields.KeywordField(normalizer=lowercase_normalizer),
        }
    )

    nuts_levels = fields.NestedField(
        properties={
            'name': fields.KeywordField(normalizer=lowercase_normalizer),
        }
    )

    fk_relation_fields = [
        'country', 'data_type', 'data_set', 'data_source', 'info_level', 'topic_category', 'resource_type',
    ]

    def get_queryset(self):
        return super().get_queryset().select_related(
            *self.fk_relation_fields
        )

    class Meta:
        model = Document
        fields = [
            'id',
            'published_year',
            'data_collection_start_year',
            'data_collection_end_year',
            'next_update_year',
        ]
