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
    SearchViewSet
)


facets_router = routers.SimpleRouter()
facets_router.register('info-level', InfoLevelViewSet, base_name='info-level')
facets_router.register('country', CountryViewSet, base_name='country')
facets_router.register('data-type', DataTypeViewSet, base_name='data-type')
facets_router.register('data-set', DataSetViewSet, base_name='data-set')
facets_router.register('resource-type', ResourceTypeViewSet, base_name='resource-type')
facets_router.register('topic-category', TopicCategoryViewSet, base_name='topic-category')
facets_router.register('nuts-level', NUTSLevelViewSet, base_name='nuts-level')
facets_router.register('keyword', KeywordViewSet, base_name='keyword')
facets_router.register('language', LanguageViewSet, base_name='language')


search_router = routers.SimpleRouter()
search_router.register('search', SearchViewSet, base_name='search')
