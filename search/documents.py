from django.conf import settings
from django_elasticsearch_dsl import DocType, Index, fields
from elasticsearch_dsl.analysis import analyzer, normalizer
from elasticsearch_dsl import tokenizer, FacetedSearch, TermsFacet
from search.models import Document


nfi = Index('nfi')
nfi.settings(max_result_window=settings.MAX_RESULT_WINDOW)

lowercase_normalizer = normalizer(
    type='custom',
    name_or_instance='lowercase_normalizer',
    char_filter=[],
    filter='lowercase',
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
        analyzer='standard',
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


class DocSearch(FacetedSearch):
    doc_types = [DocumentDoc]
    fields = ['title', 'description', 'text']
    facets = {
        'country': TermsFacet(field='country'),
        'data_type': TermsFacet(field='data_type'),
        'data_set': TermsFacet(field='data_set'),
        'data_source': TermsFacet(field='data_source'),
        'info_level': TermsFacet(field='info_level'),
        'topic_category': TermsFacet(field='topic_category'),
        'resource_type': TermsFacet(field='resource_type'),
        # TODO: Find a way to use nested facets
        'keywords': TermsFacet(field='keywords.name'),
        'nuts_levels': TermsFacet(field='nuts_levels.name')
    }

    def search(self):
        s = super().search()
        return s.source(['id', 'title'])
