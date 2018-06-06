from django.conf import settings
from django_elasticsearch_dsl import DocType, Index, fields
from elasticsearch_dsl.analysis import analyzer, normalizer
from elasticsearch_dsl import tokenizer
from search.models import Document


nfi = Index('nfi')
nfi.settings(max_result_window=settings.MAX_RESULT_WINDOW)

case_insensitive_analyzer = analyzer(
    'case_insensitive_analyzer',
    tokenizer=tokenizer('trigram', 'nGram', min_gram=3, max_gram=3),
    filter=['lowercase']
)

case_insensitive_normalizer = normalizer(
    type="custom",
    name_or_instance='case_insensitive_normalizer',
    char_filter=[],
    filter="lowercase",
)


@nfi.doc_type
class DocumentDoc(DocType):
    title = fields.TextField(
        analyzer=case_insensitive_analyzer,
        fielddata=True,
        fields={'raw': fields.KeywordField(
                                multi=True,
                                ignore_above=256,
                                normalizer=case_insensitive_normalizer
        )}
    )
    country = fields.TextField(
        analyzer=case_insensitive_analyzer,
        attr='country.name',
        fielddata=True,
        fields={'raw': fields.KeywordField(
                                attr='country.name',
                                multi=True,
                                ignore_above=256,
                                normalizer=case_insensitive_normalizer
        )}
    )
    country_id = fields.KeywordField(attr='country.id')
    data_type = fields.TextField(
        analyzer=case_insensitive_analyzer,
        attr='data_type.name',
        fielddata=True,
        fields={'raw': fields.KeywordField(
                                attr='data_type.name',
                                multi=True,
                                ignore_above=256,
                                normalizer=case_insensitive_normalizer
        )}
    )
    data_set = fields.TextField(
        analyzer=case_insensitive_analyzer,
        attr='data_set.name',
        fielddata=True,
        fields={'raw': fields.KeywordField(
                                attr='data_set.name',
                                multi=True,
                                ignore_above=256,
                                normalizer=case_insensitive_normalizer
        )}
    )
    resource_type = fields.TextField(
        analyzer=case_insensitive_analyzer,
        attr='resource_type.name',
        fielddata=True,
        fields={'raw': fields.KeywordField(
                                attr='resource_type.name',
                                multi=True,
                                ignore_above=256,
                                normalizer=case_insensitive_normalizer
        )}
    )
    info_level = fields.TextField(
        analyzer=case_insensitive_analyzer,
        attr='info_level.name',
        fielddata=True,
        fields={'raw': fields.KeywordField(
                                attr='info_level.name',
                                multi=True,
                                ignore_above=256,
                                normalizer=case_insensitive_normalizer
        )}
    )
    topic_category = fields.TextField(
        analyzer=case_insensitive_analyzer,
        attr='topic_category.name',
        fielddata=True,
        fields={'raw': fields.KeywordField(
                                attr='topic_category.name',
                                multi=True,
                                ignore_above=256,
                                normalizer=case_insensitive_normalizer
        )}
    )

    class Meta:
        model = Document
        fields = [
            'id',
            'description',
            'published_year',
            'data_collection_start_year',
            'data_collection_end_year',
            'next_update_year',
            'additional_info'
        ]
