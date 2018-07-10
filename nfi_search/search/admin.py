from django.contrib import admin
from .models import (
    DCountry, DDataSet, DLanguage, DResourceType,
    DTopicCategory, DDataSource, DDataType, DInfoLevel,
    DKeyword, DNutsLevel, DFileType, Organization,  Document, DocumentFile,
    GeographicBounds, CountryData,
)


class DCountryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id', 'name', 'code']


class DResourceTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id', 'name']


class DDataSetAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id', 'name']


class DLanguageAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id', 'name']


class DTopicCategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id', 'name']


class DDataSourceAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id', 'name']


class DDataTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id', 'name']


class DInfoLevelAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id', 'name', 'description']


class DKeywordAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id', 'name']


class DNutsLevelAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id', 'name', 'description', 'level']


class DFileTypeAdmin(admin.ModelAdmin):
    search_fields = ['name', 'media_type']
    list_display = ['id', 'name', 'media_type']


class OrganizationAdmin(admin.ModelAdmin):
    search_fields = ['name', 'responsible_person', 'email']
    list_display = ['id', 'name', 'responsible_person', 'email']


class DocumentAdmin(admin.ModelAdmin):
    search_fields = ['title', ]
    list_display = ['id', 'title', 'country']


class DocumentFileAdmin(admin.ModelAdmin):
    list_display = ['name', 'extension', 'size']


class GeographicBoundsAdmin(admin.ModelAdmin):
    list_display = ['document', 'bound_north', 'bound_east', 'bound_south',
                    'bound_west']


class CountryDataAdmin(admin.ModelAdmin):
    list_display = ['country', 'source_name', 'source_type']


admin.site.register(DCountry, DCountryAdmin)
admin.site.register(DResourceType, DResourceTypeAdmin)
admin.site.register(DDataSet, DDataSetAdmin)
admin.site.register(DLanguage, DLanguageAdmin)
admin.site.register(DTopicCategory, DTopicCategoryAdmin)
admin.site.register(DDataSource, DDataSourceAdmin)
admin.site.register(DDataType, DDataTypeAdmin)
admin.site.register(DInfoLevel, DInfoLevelAdmin)
admin.site.register(DKeyword, DKeywordAdmin)
admin.site.register(DNutsLevel, DNutsLevelAdmin)
admin.site.register(DFileType, DFileTypeAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentFile, DocumentFileAdmin)
admin.site.register(GeographicBounds, GeographicBoundsAdmin)
admin.site.register(CountryData, CountryDataAdmin)
