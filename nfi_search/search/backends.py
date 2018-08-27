from django.core.exceptions import ImproperlyConfigured
from django_elasticsearch_dsl_drf.filter_backends import (
    FacetedSearchFilterBackend,
    FilteringFilterBackend,
)
from django_elasticsearch_dsl_drf.constants import (
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_RANGE,
    LOOKUP_QUERY_GT,
    LOOKUP_QUERY_GTE,
    LOOKUP_QUERY_LT,
    LOOKUP_QUERY_LTE,
)
from elasticsearch_dsl.query import Q, Nested, Terms, Range

from django_elasticsearch_dsl_drf.constants import ALL_LOOKUP_FILTERS_AND_QUERIES

__all__ = ("NestedFacetedSearchFilterBackend",)


class NestedFacetedSearchFilterBackend(
    FacetedSearchFilterBackend, FilteringFilterBackend
):
    """
    Adds nesting to keywords and NUTS levels.

    Implemented as workaround until issue

        https://github.com/barseghyanartur/django-elasticsearch-dsl-drf/issues/52

    is resolved.

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
                nested_path = self.get_filter_field_nested_path(
                    nested_filter_fields, field_name
                )

                if lookup_param is None or lookup_param in valid_lookups:
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
                                **nested_faceted_fields[__field]["options"]
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
                    if (
                        __facet["filter_field"] == options["field"] or
                        __facet["filter_field"] == options.get("filter_field")
                    ):  # Don't filter nested aggregation on its own field
                        continue
                else:
                    if (
                        __field == options["field"] or
                        __field == options.get("filter_field")
                    ):  # Don't filter aggregation on its own field
                        continue

                if (
                    isinstance(options["values"], (list, tuple))
                    and options["lookup"] is None
                ):
                    if "path" in options:  # Filter term is nested
                        agg_filter &= Nested(
                            path=options["path"],
                            query=Terms(**{options["field"]: options["values"]})
                        )
                    else:
                        agg_filter &= Q("terms", **{options["field"]: options["values"]})
                    continue

                lookup_filter = Q("match_all")
                for value in options['values']:
                    # `terms` filter lookup
                    if options["lookup"] == LOOKUP_FILTER_TERMS:
                        lookup_filter &= Q("terms", **{options["field"]: self.split_lookup_complex_value(value)})
                    # `range` filter lookup
                    elif options["lookup"] == LOOKUP_FILTER_RANGE:
                        lookup_filter &= Q("range", **{options["field"]: self.get_range_params(value)})
                    elif options["lookup"] == LOOKUP_QUERY_GT:
                        lookup_filter &= Q("range", **{options['field']: self.get_gte_lte_params(value, 'gt')})
                    elif options["lookup"] == LOOKUP_QUERY_GTE:
                        lookup_filter &= Q("range", **{options['field']: self.get_gte_lte_params(value, 'gte')})
                    elif options["lookup"] == LOOKUP_QUERY_LT:
                        lookup_filter &= Q("range", **{options['field']: self.get_gte_lte_params(value, 'lt')})
                    elif options["lookup"] == LOOKUP_QUERY_LTE:
                        lookup_filter &= Q("range", **{options['field']: self.get_gte_lte_params(value, 'lte')})

                if "path" in options:  # Filter term is nested
                    agg_filter &= Nested(
                        path=options["path"],
                        query=lookup_filter)
                else:
                    agg_filter &= lookup_filter

            if nested_facet:
                if global_facet:
                    queryset.aggs.bucket(
                        "_filter_" + __field, "global"
                    ).bucket(
                        # Filter must appear BEFORE nested aggregation to have effect
                        "_filter_" + __field, "filter", filter=agg_filter
                    ).bucket(
                        "_filter_" + __field, "nested", path=__facet["path"],
                    ).bucket(__field, agg)
                else:
                    queryset.aggs.bucket(
                        "_filter_" + __field, "filter", filter=agg_filter
                    ).bucket(
                        "_filter_" + __field, "nested", path=__facet["path"]
                    ).bucket(__field, agg)
            else:
                if global_facet:
                    queryset.aggs.bucket(
                        "_filter_" + __field, "global"
                    ).bucket(
                        "_filter_" + __field, "filter", filter=agg_filter
                    ).bucket(__field, agg)
                else:
                    queryset.aggs.bucket(
                        "_filter_" + __field, "filter", filter=agg_filter
                    ).bucket(__field, agg)

        return queryset
