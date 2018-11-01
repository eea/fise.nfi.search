from django.conf import settings
from django_elasticsearch_dsl import DocType, Index, fields
from elasticsearch_dsl.analysis import analyzer, normalizer, char_filter, token_filter
from .models import Document, DKeyword


nfi = Index(settings.ELASTICSEARCH_INDEX)
nfi.settings(max_result_window=settings.MAX_RESULT_WINDOW)

lowercase_normalizer = normalizer(
    type="custom",
    name_or_instance="lowercase_normalizer",
    char_filter=[],
    filter="lowercase",
)

no_digits_char_filter = char_filter(
    name_or_instance="no_digits", type="pattern_replace", pattern="(\\d+)", replace=""
)

no_digits_analyzer = analyzer(
    name_or_instance="no_digits",
    tokenizer="standard",
    filter=["standard", "lowercase", "stop"],
    char_filter=[no_digits_char_filter],
)


def _autophrase_term(term):
    return "_".join(term.split(" "))


def _autophrased_synonyms(terms):
    return [f"{t} => {_autophrase_term(t)}" for t in terms]


def _keywords_filter(keywords):
    return token_filter(
        "keywords_autophrase_syn",
        type="synonym",
        synonyms=_autophrased_synonyms(keywords),
    )


def _keywords_analyzer(keywords):
    return analyzer(
        name_or_instance="keywords_analyzer",
        tokenizer="lowercase",
        filter=[_keywords_filter(keywords)],
    )


def _get_keywords():
    return [kw.name.strip().lower() for kw in DKeyword.objects.all()]


keywords_analyzer = _keywords_analyzer(_get_keywords())


@nfi.doc_type
class DocumentDoc(DocType):

    title = fields.TextField(analyzer="standard", boost=5.0, fielddata=True)

    description = fields.TextField(analyzer="standard", boost=2.0, fielddata=True)

    text = fields.TextField(analyzer=no_digits_analyzer, fielddata=True)

    countries = fields.NestedField(
        properties={"name": fields.KeywordField(normalizer=lowercase_normalizer)}
    )

    data_type = fields.KeywordField(
        attr="data_type.name", normalizer=lowercase_normalizer
    )

    data_set = fields.KeywordField(
        attr="data_set.name", normalizer=lowercase_normalizer
    )

    data_source = fields.KeywordField(
        attr="data_source.name", normalizer=lowercase_normalizer
    )

    info_level = fields.KeywordField(
        attr="info_level.name", normalizer=lowercase_normalizer
    )

    resource_type = fields.KeywordField(
        attr="resource_type.name", normalizer=lowercase_normalizer
    )

    topic_category = fields.KeywordField(
        attr="topic_category.name", normalizer=lowercase_normalizer
    )

    external_link = fields.TextField(
        attr="file.external_link", fielddata=True
    )

    organization_name = fields.TextField(
        attr="organization.name", fielddata=True
    )

    organization_email = fields.TextField(
        attr="organization.email", fielddata=True
    )

    keywords = fields.NestedField(
        properties={
            "name": fields.StringField(
                analyzer=keywords_analyzer,
                fields={
                    "name": fields.KeywordField()
                }
            )
        }
    )

    nuts_levels = fields.NestedField(
        properties={"name": fields.KeywordField(normalizer=lowercase_normalizer)}
    )

    fk_relation_fields = [
        "data_type",
        "data_set",
        "data_source",
        "info_level",
        "topic_category",
        "resource_type",
        "organization",
        "file",
    ]

    def get_queryset(self):
        return super().get_queryset().select_related(*self.fk_relation_fields)

    class Meta:
        model = Document
        fields = [
            "id",
            "published_year",
            "data_collection_start_year",
            "data_collection_end_year",
            "next_update_year",
        ]
