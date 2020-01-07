from rest_framework import routers
from .views import (
    InfoLevelViewSet,
    CountryViewSet,
    DataSetViewSet,
    DataTypeViewSet,
    ResourceTypeViewSet,
    TopicCategoryViewSet,
    NUTSLevelViewSet,
    KeywordViewSet,
    LanguageViewSet,
    SearchViewSet,
    DocumentViewSet,
    CollectionYearsRangeViewSet,
    PublicationYearsViewSet,
)


facets_router = routers.SimpleRouter()
facets_router.register('facets/info-level', InfoLevelViewSet, basename='info-level')
facets_router.register('facets/country', CountryViewSet, basename='country')
facets_router.register('facets/data-type', DataTypeViewSet, basename='data-type')
facets_router.register('facets/data-set', DataSetViewSet, basename='data-set')
facets_router.register('facets/resource-type', ResourceTypeViewSet, basename='resource-type')
facets_router.register('facets/topic-category', TopicCategoryViewSet, basename='topic-category')
facets_router.register('facets/nuts-level', NUTSLevelViewSet, basename='nuts-level')
facets_router.register('facets/keyword', KeywordViewSet, basename='keyword')
facets_router.register('facets/language', LanguageViewSet, basename='language')

docs_router = routers.SimpleRouter()
docs_router.register(
    'documents',
    DocumentViewSet,
    basename='document'
)

search_router = routers.SimpleRouter()
search_router.register('search', SearchViewSet, basename='search')

collections_range = routers.SimpleRouter()
collections_range.register('collections_range', CollectionYearsRangeViewSet, basename='collections_range')

publication_years = routers.SimpleRouter()
publication_years.register('publication_years', PublicationYearsViewSet, basename='publication_years')

main_routers = (
    facets_router,
    docs_router,
    search_router,
    collections_range,
    publication_years,
)
