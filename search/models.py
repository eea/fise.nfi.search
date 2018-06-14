from django.db import models
import attr

from .metadata import prepare_data, update_data


class DictionaryMixin:

    @classmethod
    def update_from_metadata(cls, records):
        data = prepare_data(cls, 'name', cls.metadata_field, records)
        return update_data(cls, 'name', data)


class DCountry(models.Model):
    name = models.CharField(max_length=256, unique=True)
    code = models.CharField(max_length=50)

    class Meta:
        db_table = 'd_country'
        verbose_name_plural = 'DCountries'

    def __str__(self):
        return self.name

    @classmethod
    def update_from_metadata(cls, records):
        """Countries are a peculiar import case, as they come with ids in the metadata."""
        countries = {
            r.country_id: r.country
            for r in records
            if r.country_id is not None and r.country is not None
        }
        existing = cls.objects.filter(id__in=countries.keys())
        for c in existing:
            countries.pop(c.pk, None)

        orig_count = cls.objects.count()
        objs = [cls(id=id, name=name) for id, name in countries.items()]
        cls.objects.bulk_create(objs, batch_size=100)
        return cls.objects.count() - orig_count


class DResourceType(DictionaryMixin, models.Model):
    name = models.CharField(max_length=256, unique=True)

    metadata_field = 'resource_type'

    class Meta:
        db_table = 'd_resource_type'
        verbose_name_plural = 'DResourceTypes'

    def __str__(self):
        return self.name


class DDataSet(DictionaryMixin, models.Model):
    name = models.CharField(max_length=256, unique=True)

    metadata_field = 'data_set'

    class Meta:
        db_table = 'd_data_set'
        verbose_name_plural = 'DDataSets'

    def __str__(self):
        return self.name


class DLanguage(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        db_table = 'd_language'
        verbose_name_plural = 'DLanguages'

    def __str__(self):
        return self.name

    @classmethod
    def update_from_metadata(cls, records):
        data = set([lang for r in records for lang in r.languages])
        existing = [o.name for o in cls.objects.only('name').filter(name__in=data)]
        data = [d for d in data if d not in existing]
        return update_data(cls, 'name', data)


class DTopicCategory(DictionaryMixin, models.Model):
    name = models.CharField(max_length=256, unique=True)

    metadata_field = 'topic_category'

    class Meta:
        db_table = 'd_topic_category'
        verbose_name_plural = 'DTopicCategories'

    def __str__(self):
        return self.name


class DDataSource(DictionaryMixin, models.Model):
    name = models.CharField(max_length=256, unique=True)

    metadata_field = 'data_source'

    class Meta:
        db_table = 'd_data_source'
        verbose_name_plural = 'DDataSources'

    def __str__(self):
        return self.name


class DDataType(DictionaryMixin, models.Model):
    name = models.CharField(max_length=256, unique=True)

    metadata_field = 'data_type'

    class Meta:
        db_table = 'd_data_type'
        verbose_name_plural = 'DDataTypes'

    def __str__(self):
        return self.name


class DInfoLevel(DictionaryMixin, models.Model):
    name = models.CharField(max_length=256, unique=True)
    description = models.TextField()

    metadata_field = 'info_level'

    class Meta:
        db_table = 'd_info_level'
        verbose_name_plural = 'DInfoLevels'

    def __str__(self):
        return self.name


class DKeyword(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        db_table = 'd_keyword'
        verbose_name_plural = 'DKeywords'

    def __str__(self):
        return self.name

    @classmethod
    def update_from_metadata(cls, records):
        """
        The keyword-specific columns are ignored, and keywords are extracted
        from the concatenated keyword columns ('KEYWORDS' and 'ADDITIONAL_INFO').
        """
        data = set(
            [w for r in records for w in r.keywords] +
            [w for r in records for w in r.additional_info]
        )

        existing = [o.name for o in cls.objects.only('name').filter(name__in=data)]
        data = [d for d in data if d not in existing]
        return update_data(cls, 'name', data)


class DNutsLevel(models.Model):
    name = models.CharField(max_length=256, unique=True)
    description = models.TextField()
    level = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'd_nuts_level'
        verbose_name_plural = 'DNutsLevels'

    def __str__(self):
        return self.name

    @classmethod
    def update_from_metadata(cls, records):
        data = set([level for r in records for level in r.nuts_levels])
        existing = [o.name for o in cls.objects.only('name').filter(name__in=data)]
        data = [d for d in data if d not in existing]
        return update_data(cls, 'name', data)


class DFileType(models.Model):
    name = models.CharField(max_length=256, unique=True)
    media_type = models.TextField()

    class Meta:
        db_table = 'd_file_type'
        verbose_name_plural = 'DFileTypes'

    def __str__(self):
        return self.name

    @classmethod
    def update_from_metadata(cls, records):
        data = set()
        for r in records:
            if r.resource_locator_internal is not None:
                ext = r.resource_locator_internal.split('.')[-1].strip().lower()
                if ext:
                    data.add(ext)

        existing = [o.name for o in cls.objects.only('name').filter(name__in=data)]
        data = [d for d in data if d not in existing]
        return update_data(cls, 'name', data)


class Organization(models.Model):
    name = models.TextField(blank=True, null=True)
    responsible_person = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'organization'

    def __str__(self):
        return self.name

    @classmethod
    def update_from_metadata(cls, records):
        # Organization.responsible_person is not populated, as the Excel data
        # seems to include that in the email column, with no consistent format.
        orgs = set(
            [
                (r.organization, r.organization_email)
                for r in records
                if r.organization is not None
            ]
        )

        new = 0
        for o in orgs:
            if not cls.objects.filter(name=o[0], email=o[1]).exists():
                cls.objects.create(name=o[0], email=o[1])
                new += 1
        return new


class Document(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True)
    country = models.ForeignKey(DCountry, blank=True, null=True)
    data_type = models.ForeignKey(DDataType, blank=True, null=True)
    data_set = models.ForeignKey(DDataSet, blank=True, null=True)
    resource_type = models.ForeignKey(DResourceType, blank=True, null=True)
    info_level = models.ForeignKey(DInfoLevel, blank=True, null=True)
    topic_category = models.ForeignKey(DTopicCategory, blank=True, null=True)
    keywords = models.ManyToManyField(
        DKeyword, related_name='documents', db_table='document_keyword'
    )
    data_source = models.ForeignKey(DDataSource, blank=True, null=True)
    organization = models.ForeignKey(Organization, blank=True, null=True)
    published_year = models.IntegerField(blank=True, null=True)
    data_collection_start_year = models.IntegerField(blank=True, null=True)
    data_collection_end_year = models.IntegerField(blank=True, null=True)
    next_update_year = models.IntegerField(blank=True, null=True)
    nuts_levels = models.ManyToManyField(
        DNutsLevel, related_name='documents', db_table='document_nuts_level'
    )
    # TODO: Discuss dropping this, as terms here are conflated with keywords contents
    additional_info = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'document'

    def __str__(self):
        return self.title

    @classmethod
    def save_metadata_record(cls, rec_id, records, processed_ids=None):
        processed_ids = processed_ids or []
        if rec_id not in processed_ids:
            rec = records[rec_id]
            parent = None
            if rec.parent_id is not None and rec.parent_id not in processed_ids:
                parent, processed_ids = cls.save_metadata_record(
                    rec.parent_id, records, processed_ids
                )

            doc = attr.asdict(rec)
            doc = {
                field: value
                for field, value in doc.items()
                if field in rec.relevant_fields()
            }

            # Prepare FK relations
            doc['parent'] = parent

            # Map dictionary relation name to a tuple of:
            # <related model>, (<related model field 1>, <corresponding metadata field 1>, ...)
            # The specified related model fields must be able to uniquely identify the related instance.
            fk_rels = {
                'country': (DCountry, (('name', 'country'),)),
                'data_type': (DDataType, (('name', 'data_type'),)),
                'data_set': (DDataSet, (('name', 'data_set'),)),
                'resource_type': (DResourceType, (('name', 'resource_type'),)),
                'info_level': (DInfoLevel, (('name', 'info_level'),)),
                'topic_category': (DTopicCategory, (('name', 'topic_category'),)),
                'data_source': (DDataSource, (('name', 'data_source'),)),
                'organization': (
                    Organization,
                    (('name', 'organization'), ('email', 'organization_email')),
                ),
            }

            for relation, details in fk_rels.items():
                model, field_pairs = details
                relation_filter = {p[0]: doc[p[1]] for p in field_pairs}
                if any(relation_filter.values()):
                    try:
                        doc[relation] = model.objects.get(**relation_filter)
                    except model.DoesNotExist:
                        print(
                            f'row={rec_id} {relation_filter} not found in {model.__name__}'
                        )
                        return None, processed_ids
                else:
                    doc.pop(relation, None)

            # Remove non-Document fields (e.g. 'organization_email')
            discard_fields = [p[1] for v in fk_rels.values() for p in v[1] if p[1] not in fk_rels.keys()]
            for f in discard_fields:
                doc.pop(f)

            # Pop off M2M raw data before creating doc (M2M needs id)
            nuts_levels = doc.pop('nuts_levels', [])
            keywords = doc.pop('keywords', [])
            additional_info = doc.pop('additional_info', [])
            location = doc.pop('resource_locator_internal', None)
            external_link = doc.pop('resource_locator_external', None)
            languages = doc.pop('languages', [])
            geo_fields = ('bound_north', 'bound_east', 'bound_south', 'bound_west', 'projection', 'spatial_resolution')
            geo_bounds = {field: doc.pop(field, None) for field in geo_fields}

            doc = Document.objects.create(**doc)

            # Add M2M relations
            nuts_levels = DNutsLevel.objects.filter(name__in=nuts_levels)
            keywords = DKeyword.objects.filter(name__in=set(keywords + additional_info))
            doc.nuts_levels = nuts_levels
            doc.keywords = keywords
            doc.save()

            # Create geo bounds if available
            if any(v for v in geo_bounds.values()):
                geo_bounds['document'] = doc
                GeographicBounds.objects.create(**geo_bounds)

            # Create file and associate languages
            if location is not None or external_link is not None:
                file = File.objects.create(document=doc, location=location, external_link=external_link)
                if languages:
                    languages = DLanguage.objects.filter(name__in=languages)
                    file.languages = languages
                    file.save()

            processed_ids.append(rec_id)
            return doc, processed_ids

        return None, processed_ids

    @classmethod
    def save_metadata_records(cls, records):
        """Creates `Document`s from a list of `MetadataRecord`s"""
        records = {r.id: r for r in records}
        processed_ids = []
        for rec_id, rec in records.items():
            _, processed_ids = cls.save_metadata_record(rec_id, records, processed_ids)


class File(models.Model):
    document = models.ForeignKey(Document, blank=True, null=True, related_name='file')
    location = models.TextField(blank=True, null=True)
    external_link = models.TextField(blank=True, null=True)
    file_size = models.IntegerField(blank=True, null=True)
    file_type = models.ForeignKey(DFileType, blank=True, null=True)
    languages = models.ManyToManyField(
        DLanguage, related_name='files', db_table='file_language'
    )

    class Meta:
        db_table = 'file'

    def __str__(self):
        return self.external_link


class GeographicBounds(models.Model):
    document = models.ForeignKey(Document, blank=True, null=True, related_name='geo_bounds')
    bound_north = models.DecimalField(
        max_digits=15, decimal_places=6, blank=True, null=True
    )
    bound_east = models.DecimalField(
        max_digits=15, decimal_places=6, blank=True, null=True
    )
    bound_south = models.DecimalField(
        max_digits=15, decimal_places=6, blank=True, null=True
    )
    bound_west = models.DecimalField(
        max_digits=15, decimal_places=6, blank=True, null=True
    )
    projection = models.TextField(blank=True, null=True)
    spatial_resolution = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'geographic_bounds'
        verbose_name_plural = 'GeographicBounds'

    def __str__(self):
        return '{} - N:{}, E:{}, S:{}, W:{}'.format(
            self.document.title,
            self.bound_north,
            self.bound_east,
            self.bound_south,
            self.bound_west,
        )


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
