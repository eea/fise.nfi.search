from django_elasticsearch_dsl_drf.filter_backends import (
    FacetedSearchFilterBackend,
    FilteringFilterBackend,
)
from django_elasticsearch_dsl_drf.constants import LOOKUP_FILTER_TERMS
from elasticsearch_dsl.query import Q

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

    def filter_queryset(self, request, queryset, view):
        queryset = super().filter_queryset(request, queryset, view)

        queryset.aggs.bucket("_filter_country", "nested", path="countries").bucket(
            "country", "terms", field="countries.name"
        )

        queryset.aggs.bucket("_filter_nuts_level", "nested", path="nuts_levels").bucket(
            "nuts_level", "terms", field="nuts_levels.name"
        )

        queryset.aggs.bucket("_filter_keyword", "nested", path="keywords").bucket(
            "keyword", "terms", field="keywords.name"
        )

        return queryset

    def aggregate(self, request, queryset, view):
        __facets = self.construct_facets(request, view)
        filter_query_params = self.get_filter_query_params(request, view).values()
        for __field, __facet in __facets.items():
            agg = __facet["facet"].get_aggregation()
            agg_filter = Q("match_all")

            for options in filter_query_params:
                if __field == options["field"]:
                    continue

                if (
                    isinstance(options["values"], (list, tuple))
                    and options["lookup"] is None
                ):
                    agg_filter &= Q("terms", **{options["field"]: options["values"]})
                    continue

                for value in options["values"]:
                    if options["lookup"] == LOOKUP_FILTER_TERMS:
                        agg_filter &= Q("terms", **{options["field"]: value})

            if __facet["global"]:
                queryset.aggs.bucket("_filter_" + __field, "global").bucket(
                    "_filter_" + __field, "filter", filter=agg_filter
                ).bucket(__field, agg)
            else:
                queryset.aggs.bucket(
                    "_filter_" + __field, "filter", filter=agg_filter
                ).bucket(__field, agg)

        return queryset
