import operator
from functools import reduce
from django.core.exceptions import ImproperlyConfigured
from django_elasticsearch_dsl_drf.filter_backends import (
    FacetedSearchFilterBackend,
    FilteringFilterBackend,
)
from django_elasticsearch_dsl_drf.constants import (
    LOOKUP_FILTER_PREFIX,
    LOOKUP_FILTER_RANGE,
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_EXISTS,
    LOOKUP_FILTER_WILDCARD,
    LOOKUP_QUERY_CONTAINS,
    LOOKUP_QUERY_IN,
    LOOKUP_QUERY_GT,
    LOOKUP_QUERY_GTE,
    LOOKUP_QUERY_LT,
    LOOKUP_QUERY_LTE,
    LOOKUP_QUERY_STARTSWITH,
    LOOKUP_QUERY_ENDSWITH,
    LOOKUP_QUERY_ISNULL,
    LOOKUP_QUERY_EXCLUDE,
)

from elasticsearch_dsl.query import Q, Nested, Terms, MatchPhrase
from django_elasticsearch_dsl_drf.filter_backends import NestedFilteringFilterBackend
from django_elasticsearch_dsl_drf.constants import ALL_LOOKUP_FILTERS_AND_QUERIES

__all__ = (
    "NestedFacetedSearchFilterBackend",
    "DefaultAwareNestedFilteringFilterBackend",
    "LOOKUP_QUERY_MATCH_PHRASE",
)


LOOKUP_QUERY_MATCH_PHRASE = "match_phrase"


class NestedFacetedSearchFilterBackend(
    FacetedSearchFilterBackend, FilteringFilterBackend
):
    """
    Adds nesting to keywords and NUTS levels.

    Implemented as workaround until issue

        https://github.com/barseghyanartur/django-elasticsearch-dsl-drf/issues/52

    is resolved.

    The 'default_lookup' option for nested filter fields is honored.

    There is no toggling of facets using query params, the facets are always on.

    Global aggregations are filtered on all fields except the one currently being aggregated.
    """

    @classmethod
    def prepare_nested_filter_fields(cls, view):
        if not hasattr(view, "nested_filter_fields"):
            raise ImproperlyConfigured(
                "You need to define `nested_filter_fields` in your `{}` view "
                "when using `{}` filter backend."
                "".format(view.__class__.__name__, cls.__name__)
            )

        filter_fields = view.nested_filter_fields

        for field, options in filter_fields.items():
            if options is None or isinstance(options, str):
                filter_fields[field] = {"field": options or field}
            elif "field" not in filter_fields[field]:
                filter_fields[field]["field"] = field

            if "lookups" not in filter_fields[field]:
                filter_fields[field]["lookups"] = tuple(ALL_LOOKUP_FILTERS_AND_QUERIES)

        return filter_fields

    @staticmethod
    def get_filter_field_nested_path(filter_fields, field_name):
        if "path" in filter_fields[field_name]:
            return filter_fields[field_name]["path"]
        return field_name

    def get_filter_query_params(self, request, view):
        query_params = request.query_params.copy()

        filter_query_params = {}
        filter_fields = self.prepare_filter_fields(view)
        nested_filter_fields = self.prepare_nested_filter_fields(view)

        for query_param in query_params:
            query_param_list = self.split_lookup_filter(query_param, maxsplit=1)
            field_name = query_param_list[0]
            if field_name in filter_fields:
                lookup_param = None
                if len(query_param_list) > 1:
                    lookup_param = query_param_list[1]

                valid_lookups = filter_fields[field_name]["lookups"]
                # If we have default lookup given use it as a default and
                # do not require further suffix specification.
                default_lookup = None
                if "default_lookup" in filter_fields[field_name]:
                    default_lookup = filter_fields[field_name]["default_lookup"]

                if lookup_param is None or lookup_param in valid_lookups:

                    # If we have default lookup given use it as a default
                    # and do not require further suffix specification.
                    if lookup_param is None and default_lookup is not None:
                        lookup_param = str(default_lookup)

                    values = [
                        __value.strip()
                        for __value in query_params.getlist(query_param)
                        if __value.strip() != ""
                    ]

                    if values:
                        filter_query_params[query_param] = {
                            "lookup": lookup_param,
                            "values": values,
                            "field": filter_fields[field_name].get("field", field_name),
                            "type": view.mapping,
                        }
            elif field_name in nested_filter_fields:
                lookup_param = None
                if len(query_param_list) > 1:
                    lookup_param = query_param_list[1]

                valid_lookups = nested_filter_fields[field_name]["lookups"]
                default_lookup = nested_filter_fields[field_name].get("default_lookup")

                nested_path = self.get_filter_field_nested_path(
                    nested_filter_fields, field_name
                )

                if lookup_param is None or lookup_param in valid_lookups:

                    if lookup_param is None and default_lookup is not None:
                        lookup_param = str(default_lookup)

                    values = [
                        __value.strip()
                        for __value in query_params.getlist(query_param)
                        if __value.strip() != ""
                    ]

                    if values:
                        filter_query_params[query_param] = {
                            "lookup": lookup_param,
                            "values": values,
                            "field": nested_filter_fields[field_name].get(
                                "field", field_name
                            ),
                            "filter_field": field_name,
                            "type": view.mapping,
                            "path": nested_path,
                        }

        return filter_query_params

    def construct_nested_facets(self, request, view):
        """Construct nested facets."""
        __nested_facets = {}
        faceted_search_query_params = self.get_faceted_search_query_params(request)
        nested_faceted_fields = view.nested_faceted_search_fields
        for __field, __options in view.nested_faceted_search_fields.items():
            if __field in faceted_search_query_params or __options["enabled"]:
                __nested_facets.update(
                    {
                        __field: {
                            "facet": nested_faceted_fields[__field]["facet"](
                                field=nested_faceted_fields[__field]["field"],
                                **nested_faceted_fields[__field]["options"],
                            ),
                            "filter_field": nested_faceted_fields[__field][
                                "filter_field"
                            ],
                            "path": nested_faceted_fields[__field]["path"],
                            "global": nested_faceted_fields[__field]["global"],
                        }
                    }
                )
        return __nested_facets

    def aggregate(self, request, queryset, view):
        filter_query_params = self.get_filter_query_params(request, view).values()
        __facets = self.construct_facets(request, view)
        __nested_facets = self.construct_nested_facets(request, view)
        __facets.update(__nested_facets)
        for __field, __facet in __facets.items():
            agg = __facet["facet"].get_aggregation()
            agg_filter = Q("match_all")
            global_facet = __facet.get("global", False)
            nested_facet = "path" in __facet
            for options in filter_query_params:
                if nested_facet:
                    if __facet["filter_field"] == options["field"] or __facet[
                        "filter_field"
                    ] == options.get(
                        "filter_field"
                    ):  # Don't filter nested aggregation on its own field
                        continue
                else:
                    if __field == options["field"] or __field == options.get(
                        "filter_field"
                    ):  # Don't filter aggregation on its own field
                        continue

                if (
                    isinstance(options["values"], (list, tuple))
                    and options["lookup"] is None
                ):
                    if "path" in options:  # Filter term is nested
                        if options["path"] == "keywords":
                            for val in options["values"]:
                                agg_filter &= Nested(
                                    path=options["path"],
                                    query=MatchPhrase(**{options["field"]: val}),
                                )
                        else:
                            agg_filter &= Nested(
                                path=options["path"],
                                query=Terms(**{options["field"]: options["values"]}),
                            )
                    else:
                        agg_filter &= Q(
                            "terms", **{options["field"]: options["values"]}
                        )
                    continue

                lookup_filter = Q("match_all")
                for value in options["values"]:
                    if options["lookup"] == LOOKUP_FILTER_TERMS:
                        lookup_filter &= Q(
                            "terms",
                            **{
                                options["field"]: self.split_lookup_complex_value(value)
                            },
                        )
                    elif options["lookup"] == LOOKUP_FILTER_RANGE:
                        lookup_filter &= Q(
                            "range", **{options["field"]: self.get_range_params(value)}
                        )
                    elif options["lookup"] == LOOKUP_QUERY_GT:
                        lookup_filter &= Q(
                            "range",
                            **{options["field"]: self.get_gte_lte_params(value, "gt")},
                        )
                    elif options["lookup"] == LOOKUP_QUERY_GTE:
                        lookup_filter &= Q(
                            "range",
                            **{options["field"]: self.get_gte_lte_params(value, "gte")},
                        )
                    elif options["lookup"] == LOOKUP_QUERY_LT:
                        lookup_filter &= Q(
                            "range",
                            **{options["field"]: self.get_gte_lte_params(value, "lt")},
                        )
                    elif options["lookup"] == LOOKUP_QUERY_LTE:
                        lookup_filter &= Q(
                            "range",
                            **{options["field"]: self.get_gte_lte_params(value, "lte")},
                        )
                    elif options["lookup"] == "match_phrase":
                        lookup_filter &= MatchPhrase(**{options["field"]: value})

                if "path" in options:  # Filter term is nested
                    agg_filter &= Nested(path=options["path"], query=lookup_filter)
                else:
                    agg_filter &= lookup_filter

            if nested_facet:
                if global_facet:
                    queryset.aggs.bucket("_filter_" + __field, "global").bucket(
                        # Filter must appear BEFORE nested aggregation to have effect
                        "_filter_" + __field,
                        "filter",
                        filter=agg_filter,
                    ).bucket(
                        "_filter_" + __field, "nested", path=__facet["path"]
                    ).bucket(
                        __field, agg
                    )
                else:
                    queryset.aggs.bucket(
                        "_filter_" + __field, "filter", filter=agg_filter
                    ).bucket(
                        "_filter_" + __field, "nested", path=__facet["path"]
                    ).bucket(
                        __field, agg
                    )
            else:
                if global_facet:
                    queryset.aggs.bucket("_filter_" + __field, "global").bucket(
                        "_filter_" + __field, "filter", filter=agg_filter
                    ).bucket(__field, agg)
                else:
                    queryset.aggs.bucket(
                        "_filter_" + __field, "filter", filter=agg_filter
                    ).bucket(__field, agg)

        return queryset


class DefaultAwareNestedFilteringFilterBackend(NestedFilteringFilterBackend):
    """
    Nested filtering backend that adds two features to the builtin one:
     - honors the 'default_lookup' options
     - supports the 'match_phrase' query/lookup.
    """

    def get_filter_query_params(self, request, view):

        query_params = request.query_params.copy()

        filter_query_params = {}
        filter_fields = self.prepare_filter_fields(view)
        for query_param in query_params:
            query_param_list = self.split_lookup_filter(query_param, maxsplit=1)
            field_name = query_param_list[0]

            if field_name in filter_fields:
                lookup_param = None
                if len(query_param_list) > 1:
                    lookup_param = query_param_list[1]

                valid_lookups = filter_fields[field_name]["lookups"]
                default_lookup = filter_fields[field_name].get("default_lookup")

                nested_path = self.get_filter_field_nested_path(
                    filter_fields, field_name
                )

                if lookup_param is None or lookup_param in valid_lookups:
                    if lookup_param is None and default_lookup is not None:
                        lookup_param = str(default_lookup)

                    values = [
                        __value.strip()
                        for __value in query_params.getlist(query_param)
                        if __value.strip() != ""
                    ]

                    if values:
                        filter_query_params[query_param] = {
                            "lookup": lookup_param,
                            "values": values,
                            "field": filter_fields[field_name].get("field", field_name),
                            "type": view.mapping,
                            "path": nested_path,
                            "disjunction": filter_fields[field_name].get("disjunction", True)
                        }

        return filter_query_params

    @classmethod
    def apply_filter(cls, queryset, options=None, args=None, kwargs=None):
        if options is None:
            raise ImproperlyConfigured(
                "You should provide an `path` argument in the field options."
            )

        path = options.get("path")

        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        return queryset.query("nested", path=path, query=Q(*args, **kwargs))

    @classmethod
    def apply_filter_match_phrase(cls, queryset, options, value):
        return cls.apply_filter(
            queryset=queryset,
            options=options,
            args=["match_phrase"],
            kwargs={options["field"]: value},
        )

    @classmethod
    def apply_filter_match_phrases(cls, queryset, options, values):
        __queries = []
        for __value in values:
            __queries.append(Q("match_phrase", **{options["field"]: __value}))

        if __queries:
            queryset = cls.apply_filter(
                queryset=queryset,
                options=options,
                args=[reduce(operator.or_, __queries)],
            )

        return queryset

    def filter_queryset(self, request, queryset, view):
        filter_query_params = self.get_filter_query_params(request, view)
        for options in filter_query_params.values():
            # When no specific lookup given, in case of multiple values
            # we apply `terms` filter by default and proceed to the next
            # query param.
            if (
                isinstance(options["values"], (list, tuple))
                and options["lookup"] is None
            ):
                queryset = self.apply_filter_terms(queryset, options, options["values"])
                continue
            elif (
                isinstance(options["values"], (list, tuple))
                and options["lookup"] == LOOKUP_QUERY_MATCH_PHRASE
                and options["disjunction"]
            ):
                queryset = self.apply_filter_match_phrases(
                    queryset, options, options["values"]
                )
                continue

            # For all other cases, when we don't have multiple values,
            # we follow the normal flow.
            for value in options["values"]:
                # `terms` filter lookup
                if options["lookup"] == LOOKUP_FILTER_TERMS:
                    queryset = self.apply_filter_terms(queryset, options, value)

                # `prefix` filter lookup
                elif options["lookup"] in (
                    LOOKUP_FILTER_PREFIX,
                    LOOKUP_QUERY_STARTSWITH,
                ):
                    queryset = self.apply_filter_prefix(queryset, options, value)

                # `range` filter lookup
                elif options["lookup"] == LOOKUP_FILTER_RANGE:
                    queryset = self.apply_filter_range(queryset, options, value)

                # `exists` filter lookup
                elif options["lookup"] == LOOKUP_FILTER_EXISTS:
                    queryset = self.apply_query_exists(queryset, options, value)

                # `wildcard` filter lookup
                elif options["lookup"] == LOOKUP_FILTER_WILDCARD:
                    queryset = self.apply_query_wildcard(queryset, options, value)

                # `contains` filter lookup
                elif options["lookup"] == LOOKUP_QUERY_CONTAINS:
                    queryset = self.apply_query_contains(queryset, options, value)

                # `in` functional query lookup
                elif options["lookup"] == LOOKUP_QUERY_IN:
                    queryset = self.apply_query_in(queryset, options, value)

                # `gt` functional query lookup
                elif options["lookup"] == LOOKUP_QUERY_GT:
                    queryset = self.apply_query_gt(queryset, options, value)

                # `gte` functional query lookup
                elif options["lookup"] == LOOKUP_QUERY_GTE:
                    queryset = self.apply_query_gte(queryset, options, value)

                # `lt` functional query lookup
                elif options["lookup"] == LOOKUP_QUERY_LT:
                    queryset = self.apply_query_lt(queryset, options, value)

                # `lte` functional query lookup
                elif options["lookup"] == LOOKUP_QUERY_LTE:
                    queryset = self.apply_query_lte(queryset, options, value)

                # `endswith` filter lookup
                elif options["lookup"] == LOOKUP_QUERY_ENDSWITH:
                    queryset = self.apply_query_endswith(queryset, options, value)

                # `isnull` functional query lookup
                elif options["lookup"] == LOOKUP_QUERY_ISNULL:
                    queryset = self.apply_query_isnull(queryset, options, value)

                # `exclude` functional query lookup
                elif options["lookup"] == LOOKUP_QUERY_EXCLUDE:
                    queryset = self.apply_query_exclude(queryset, options, value)

                # `match_phrase` functional query lookup
                elif options["lookup"] == LOOKUP_QUERY_MATCH_PHRASE:
                    queryset = self.apply_filter_match_phrase(queryset, options, value)

                # `term` filter lookup. This is default if no `default_lookup`
                # option has been given or explicit lookup provided.
                else:
                    queryset = self.apply_filter_term(queryset, options, value)

        return queryset
