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
)


facets_router = routers.SimpleRouter()
facets_router.register('facets/info-level', InfoLevelViewSet, base_name='info-level')
facets_router.register('facets/country', CountryViewSet, base_name='country')
facets_router.register('facets/data-type', DataTypeViewSet, base_name='data-type')
facets_router.register('facets/data-set', DataSetViewSet, base_name='data-set')
facets_router.register('facets/resource-type', ResourceTypeViewSet, base_name='resource-type')
facets_router.register('facets/topic-category', TopicCategoryViewSet, base_name='topic-category')
facets_router.register('facets/nuts-level', NUTSLevelViewSet, base_name='nuts-level')
facets_router.register('facets/keyword', KeywordViewSet, base_name='keyword')
facets_router.register('facets/language', LanguageViewSet, base_name='language')

docs_router = routers.SimpleRouter()
docs_router.register(
    'documents',
    DocumentViewSet,
    base_name='document'
)

search_router = routers.SimpleRouter()
search_router.register('search', SearchViewSet, base_name='search')


main_routers = (
    facets_router,
    docs_router,
    search_router,
)
