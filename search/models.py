from django.db import models


class DCountry(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True)
    code = models.TextField()

    class Meta:
        db_table = 'd_country'


class DResourceType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True)

    class Meta:
        db_table = 'd_resource_type'


class DDataSet(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True)

    class Meta:
        db_table = 'd_data_set'


class DLanguage(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True)

    class Meta:
        db_table = 'd_language'


class DTopicCategory(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True)

    class Meta:
        db_table = 'd_topic_category'


class DDataSource(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True)

    class Meta:
        db_table = 'd_data_source'


class DDataType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True)

    class Meta:
        db_table = 'd_data_type'


class DInfoLevel(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True)
    description = models.TextField()

    class Meta:
        db_table = 'd_info_level'


class DKeyword(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True)

    class Meta:
        db_table = 'd_keyword'


class DNutsLevel(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True)
    description = models.TextField()
    level = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'd_nuts_level'


class DFileType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True)
    media_type = models.TextField()

    class Meta:
        db_table = 'd_file_type'


class Organization(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    responsible_person = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'organization'


class Document(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.TextField()
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', models.DO_NOTHING,
                               db_column='id_parent', blank=True, null=True)
    country = models.ForeignKey(DCountry, models.DO_NOTHING,
                                db_column='id_country', blank=True, null=True)
    data_type = models.ForeignKey(DDataType, models.DO_NOTHING,
                                  db_column='id_data_type',
                                  blank=True, null=True)
    data_set = models.ForeignKey(DDataSet, models.DO_NOTHING,
                                 db_column='id_data_set', blank=True, null=True)
    resource_type = models.ForeignKey(DResourceType, models.DO_NOTHING,
                                      db_column='id_resource_type',
                                      blank=True, null=True)
    info_level = models.ForeignKey(DInfoLevel, models.DO_NOTHING,
                                   db_column='id_info_level',
                                   blank=True, null=True)
    topic_category = models.ForeignKey(DTopicCategory, models.DO_NOTHING,
                                       db_column='id_topic_category',
                                       blank=True, null=True)
    data_source = models.ForeignKey(DDataSource, models.DO_NOTHING,
                                    db_column='id_data_source',
                                    blank=True, null=True)
    organization = models.ForeignKey(Organization, models.DO_NOTHING,
                                     db_column='id_organization',
                                     blank=True, null=True)
    published_year = models.IntegerField(blank=True, null=True)
    data_collection_start_year = models.IntegerField(blank=True, null=True)
    data_collection_end_year = models.IntegerField(blank=True, null=True)
    next_update_year = models.IntegerField(blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'document'


class File(models.Model):
    id = models.IntegerField(primary_key=True)
    document = models.ForeignKey(Document, models.DO_NOTHING,
                                 db_column='id_document', blank=True, null=True)
    external_link = models.TextField(blank=True, null=True)
    file_size = models.IntegerField(blank=True, null=True)
    file_type = models.ForeignKey(DFileType, models.DO_NOTHING,
                                  db_column='id_file_type',
                                  blank=True, null=True)

    class Meta:
        db_table = 'file'


class DocumentKeyword(models.Model):
    document = models.ForeignKey(Document, models.DO_NOTHING,
                                 db_column='id_document', primary_key=True)
    keyword = models.ForeignKey(DKeyword, models.DO_NOTHING,
                                db_column='id_keyword')

    class Meta:
        db_table = 'document_keyword'
        unique_together = (('document', 'keyword'),)


class DocumentNutsLevel(models.Model):
    document = models.ForeignKey(Document, models.DO_NOTHING,
                                 db_column='id_document', primary_key=True)
    nuts_level = models.ForeignKey(DNutsLevel, models.DO_NOTHING,
                                   db_column='id_nuts_level')

    class Meta:
        db_table = 'document_nuts_level'
        unique_together = (('document', 'nuts_level'),)


class FileLanguage(models.Model):
    file = models.ForeignKey(File, models.DO_NOTHING,
                             db_column='id_file', primary_key=True)
    language = models.ForeignKey(DLanguage, models.DO_NOTHING,
                                 db_column='id_language')

    class Meta:
        db_table = 'file_language'
        unique_together = (('file', 'language'),)


class GeographicBounds(models.Model):
    id = models.IntegerField(primary_key=True)
    document = models.ForeignKey(Document, models.DO_NOTHING,
                                 db_column='id_document', blank=True, null=True)
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


class CountryData(models.Model):
    id = models.IntegerField(primary_key=True)
    country = models.ForeignKey('DCountry', models.DO_NOTHING,
                                db_column='id_country', blank=True, null=True)
    version_date = models.DateTimeField(blank=True, null=True)
    country_code = models.TextField(blank=True, null=True)
    country_name = models.TextField(blank=True, null=True)
    source_name = models.TextField(blank=True, null=True)
    source_type = models.TextField(blank=True, null=True)
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
    contact_email = models.TextField(blank=True, null=True)
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
