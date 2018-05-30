from django.db import models


class DCountry(models.Model):
    name = models.CharField(max_length=256, unique=True)
    code = models.CharField(max_length=50)

    class Meta:
        db_table = 'd_country'
        verbose_name_plural = 'DCountries'


class DResourceType(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        db_table = 'd_resource_type'
        verbose_name_plural = 'DResourceTypes'


class DDataSet(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        db_table = 'd_data_set'
        verbose_name_plural = 'DDataSets'


class DLanguage(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        db_table = 'd_language'
        verbose_name_plural = 'DLanguages'


class DTopicCategory(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        db_table = 'd_topic_category'
        verbose_name_plural = 'DTopicCategories'


class DDataSource(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        db_table = 'd_data_source'
        verbose_name_plural = 'DDataSources'


class DDataType(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        db_table = 'd_data_type'
        verbose_name_plural = 'DDataTypes'


class DInfoLevel(models.Model):
    name = models.CharField(max_length=256, unique=True)
    description = models.TextField()

    class Meta:
        db_table = 'd_info_level'
        verbose_name_plural = 'DInfoLevels'


class DKeyword(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        db_table = 'd_keyword'
        verbose_name_plural = 'DKeywords'


class DNutsLevel(models.Model):
    name = models.CharField(max_length=256, unique=True)
    description = models.TextField()
    level = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'd_nuts_level'
        verbose_name_plural = 'DNutsLevels'


class DFileType(models.Model):
    name = models.CharField(max_length=256, unique=True)
    media_type = models.TextField()

    class Meta:
        db_table = 'd_file_type'
        verbose_name_plural = 'DFileTypes'


class Organization(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    responsible_person = models.CharField(max_length=256, blank=True, null=True)
    email = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        db_table = 'organization'


class Document(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True)
    country = models.ForeignKey(DCountry, blank=True, null=True)
    data_type = models.ForeignKey(DDataType, blank=True, null=True)
    data_set = models.ForeignKey(DDataSet, blank=True, null=True)
    resource_type = models.ForeignKey(DResourceType, blank=True, null=True)
    info_level = models.ForeignKey(DInfoLevel, blank=True, null=True)
    topic_category = models.ForeignKey(DTopicCategory, blank=True, null=True)
    data_source = models.ForeignKey(DDataSource, blank=True, null=True)
    organization = models.ForeignKey(Organization, blank=True, null=True)
    published_year = models.IntegerField(blank=True, null=True)
    data_collection_start_year = models.IntegerField(blank=True, null=True)
    data_collection_end_year = models.IntegerField(blank=True, null=True)
    next_update_year = models.IntegerField(blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'document'


class File(models.Model):
    document = models.ForeignKey(Document, blank=True, null=True)
    external_link = models.TextField(blank=True, null=True)
    file_size = models.IntegerField(blank=True, null=True)
    file_type = models.ForeignKey(DFileType, blank=True, null=True)

    class Meta:
        db_table = 'file'


class DocumentKeyword(models.Model):
    document = models.ForeignKey(Document, primary_key=True)
    keyword = models.ForeignKey(DKeyword)

    class Meta:
        db_table = 'document_keyword'
        unique_together = (('document', 'keyword'),)
        verbose_name_plural = 'DocumentKeywords'


class DocumentNutsLevel(models.Model):
    document = models.ForeignKey(Document, primary_key=True)
    nuts_level = models.ForeignKey(DNutsLevel)

    class Meta:
        db_table = 'document_nuts_level'
        unique_together = (('document', 'nuts_level'),)
        verbose_name_plural = 'DocumentNutsLevels'


class FileLanguage(models.Model):
    file = models.ForeignKey(File, primary_key=True)
    language = models.ForeignKey(DLanguage)

    class Meta:
        db_table = 'file_language'
        unique_together = (('file', 'language'),)
        verbose_name_plural = 'FileLanguages'


class GeographicBounds(models.Model):
    document = models.ForeignKey(Document, blank=True, null=True)
    bound_north = models.DecimalField(max_digits=15, decimal_places=6,
                                      blank=True, null=True)
    bound_east = models.DecimalField(max_digits=15, decimal_places=6,
                                     blank=True, null=True)
    bound_south = models.DecimalField(max_digits=15, decimal_places=6,
                                      blank=True, null=True)
    bound_west = models.DecimalField(max_digits=15, decimal_places=6,
                                     blank=True, null=True)
    projection = models.TextField(blank=True, null=True)
    spatial_resolution = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'geographic_bounds'
        verbose_name_plural = 'GeographicBounds'


class CountryData(models.Model):
    country = models.ForeignKey('DCountry', blank=True, null=True)
    version_date = models.DateTimeField(blank=True, null=True)
    country_code = models.CharField(max_length=50, blank=True, null=True)
    country_name = models.CharField(max_length=256, blank=True, null=True)
    source_name = models.CharField(max_length=256, blank=True, null=True)
    source_type = models.CharField(max_length=256, blank=True, null=True)
    release_date = models.TextField(blank=True, null=True)
    source_description = models.TextField(blank=True, null=True)
    main_url = models.TextField(blank=True, null=True)
    documentation_url = models.TextField(blank=True, null=True)
    data_url = models.TextField(blank=True, null=True)
    accessibility = models.TextField(blank=True, null=True)
    availability = models.TextField(blank=True, null=True)
    authors = models.TextField(blank=True, null=True)
    data_producer = models.TextField(blank=True, null=True)
    contact = models.TextField(blank=True, null=True)
    contact_email = models.CharField(max_length=256, blank=True, null=True)
    contact_technical = models.TextField(blank=True, null=True)
    contact_efdac = models.TextField(blank=True, null=True)
    inventory_type = models.TextField(blank=True, null=True)
    inventory_sampling_scheme = models.TextField(blank=True, null=True)
    inventory_sampling_density = models.TextField(blank=True, null=True)
    inventory_plot_area = models.TextField(blank=True, null=True)
    forest_plots = models.IntegerField(blank=True, null=True)
    inventory_comments = models.TextField(blank=True, null=True)
    spatial_coverage = models.TextField(blank=True, null=True)
    spatial_resolution = models.TextField(blank=True, null=True)
    temporal_coverage = models.TextField(blank=True, null=True)
    available_data = models.TextField(blank=True, null=True)
    other_data = models.TextField(blank=True, null=True)
    data_format = models.TextField(blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)
    int_be_weaknesses = models.TextField(blank=True, null=True)
    int_be_strengths = models.TextField(blank=True, null=True)
    int_be_comments = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'country_data'
        verbose_name_plural = 'CountryData'
