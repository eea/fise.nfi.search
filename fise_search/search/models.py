import os
from pathlib import Path, PureWindowsPath, PurePosixPath
import logging
from datetime import datetime as dt

import pytz
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.conf import settings
from django.urls import reverse
import attr
from tqdm import tqdm

from elasticsearch.exceptions import ConnectionTimeout as ESConnectionTimeout
from .metadata import prepare_data, update_data
from .text import extract_text, TextExtractionTimeout, TextExtractionError
from .utils import id_to_alpha

log = logging.getLogger(__name__)
info = log.info
debug = log.debug
warn = log.warning
error = log.error


class ImportFileNotFoundError(FileNotFoundError):
    pass


class DictionaryMixin:
    @classmethod
    def update_from_metadata(cls, records):
        data = prepare_data(cls, "name", cls.metadata_field, records)
        return update_data(cls, "name", data)


class DCountry(models.Model):
    name = models.CharField(max_length=256, unique=True)
    code = models.CharField(max_length=50)

    class Meta:
        db_table = "d_country"
        verbose_name_plural = "DCountries"

    def __str__(self):
        return self.name

    @classmethod
    def update_from_metadata(cls, records):
        data = set([country for r in records for country in r.countries])
        existing = [o.name for o in cls.objects.only("name").filter(name__in=data)]
        data = [d for d in data if d not in existing]
        return update_data(cls, "name", data)


class DResourceType(DictionaryMixin, models.Model):
    name = models.CharField(max_length=256, unique=True)

    metadata_field = "resource_type"

    class Meta:
        db_table = "d_resource_type"
        verbose_name_plural = "DResourceTypes"

    def __str__(self):
        return self.name


class DDataSet(DictionaryMixin, models.Model):
    name = models.CharField(max_length=256, unique=True)

    metadata_field = "data_set"

    class Meta:
        db_table = "d_data_set"
        verbose_name_plural = "DDataSets"

    def __str__(self):
        return self.name


class DLanguage(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        db_table = "d_language"
        verbose_name_plural = "DLanguages"

    def __str__(self):
        return self.name

    @classmethod
    def update_from_metadata(cls, records):
        data = set([lang for r in records for lang in r.languages])
        existing = [o.name for o in cls.objects.only("name").filter(name__in=data)]
        data = [d for d in data if d not in existing]
        return update_data(cls, "name", data)


class DTopicCategory(DictionaryMixin, models.Model):
    name = models.CharField(max_length=256, unique=True)

    metadata_field = "topic_category"

    class Meta:
        db_table = "d_topic_category"
        verbose_name_plural = "DTopicCategories"

    def __str__(self):
        return self.name


class DDataSource(DictionaryMixin, models.Model):
    name = models.CharField(max_length=256, unique=True)

    metadata_field = "data_source"

    class Meta:
        db_table = "d_data_source"
        verbose_name_plural = "DDataSources"

    def __str__(self):
        return self.name


class DDataType(DictionaryMixin, models.Model):
    name = models.CharField(max_length=256, unique=True)

    metadata_field = "data_type"

    class Meta:
        db_table = "d_data_type"
        verbose_name_plural = "DDataTypes"

    def __str__(self):
        return self.name


class DInfoLevel(DictionaryMixin, models.Model):
    name = models.CharField(max_length=256, unique=True)
    description = models.TextField()

    metadata_field = "info_level"

    class Meta:
        db_table = "d_info_level"
        verbose_name_plural = "DInfoLevels"

    def __str__(self):
        return self.name


class DKeyword(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        db_table = "d_keyword"
        verbose_name_plural = "DKeywords"

    def __str__(self):
        return self.name

    @classmethod
    def update_from_metadata(cls, records):
        """
        The keyword-specific columns are ignored, and keywords are extracted
        from the concatenated keyword columns ('KEYWORDS' and 'ADDITIONAL_INFO').
        """
        data = set(
            [w for r in records for w in r.keywords]
            + [w for r in records for w in r.additional_info]
        )

        existing = [o.name for o in cls.objects.only("name").filter(name__in=data)]
        data = [d for d in data if d not in existing]
        return update_data(cls, "name", data)


class DNutsLevel(models.Model):
    name = models.CharField(max_length=256, unique=True)
    description = models.TextField()
    level = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "d_nuts_level"
        verbose_name_plural = "DNutsLevels"

    def __str__(self):
        return self.name

    @classmethod
    def update_from_metadata(cls, records):
        data = set([level for r in records for level in r.nuts_levels])
        existing = [o.name for o in cls.objects.only("name").filter(name__in=data)]
        data = [d for d in data if d not in existing]
        return update_data(cls, "name", data)


class DFileType(models.Model):
    name = models.CharField(max_length=256, unique=True)
    media_type = models.TextField()

    class Meta:
        db_table = "d_file_type"
        verbose_name_plural = "DFileTypes"

    def __str__(self):
        return self.name

    @classmethod
    def update_from_metadata(cls, records):
        data = set()
        for r in records:
            if r.resource_locator_internal is not None:
                ext = r.resource_locator_internal.split(".")[-1].strip().lower()
                if ext:
                    data.add(ext)

        existing = [o.name for o in cls.objects.only("name").filter(name__in=data)]
        data = [d for d in data if d not in existing]
        return update_data(cls, "name", data)


class Organization(models.Model):
    name = models.TextField(blank=True, null=True)
    responsible_person = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "organization"

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


class DocumentImportBatch(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=200)
    original_path_root = models.CharField(max_length=200)
    posix_original_path = models.BooleanField(default=False)

    class Meta:
        db_table = "document_batch"
        verbose_name_plural = "DocumentBatches"

    @property
    def absolute_path(self):
        return Path(settings.FILES_DIR) / self.path

    def ensure_path(self):
        self.absolute_path.mkdir(parents=True, exist_ok=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            d = dt.utcnow().replace(tzinfo=pytz.utc)
            date_prefix = dt.strftime(d, "%Y%m%d")
            suffix_id = int(dt.strftime(d, "%Y%m%d%H%M%S"))
            self.path = f"{date_prefix}_{id_to_alpha(suffix_id)}"
            self.ensure_path()
        super().save(*args, **kwargs)


class Document(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    import_batch = models.ForeignKey(
        DocumentImportBatch, blank=True, null=True, on_delete=models.CASCADE
    )
    metadata_id = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    higher_level_docs = models.ManyToManyField(
        "self", related_name="lower_level_backrefs", symmetrical=False)
    same_level_docs = models.ManyToManyField(
        "self", related_name="same_level_backrefs", symmetrical=False)
    lower_level_docs = models.ManyToManyField(
        "self", related_name="higher_level_backrefs", symmetrical=False)

    countries = models.ManyToManyField(
        DCountry, related_name="documents", db_table="document_country"
    )

    data_type = models.ForeignKey(
        DDataType, blank=True, null=True, on_delete=models.SET_NULL
    )
    data_set = models.ForeignKey(
        DDataSet, blank=True, null=True, on_delete=models.SET_NULL
    )
    resource_type = models.ForeignKey(
        DResourceType, blank=True, null=True, on_delete=models.SET_NULL
    )
    info_level = models.ForeignKey(
        DInfoLevel, blank=True, null=True, on_delete=models.SET_NULL
    )
    topic_category = models.ForeignKey(
        DTopicCategory, blank=True, null=True, on_delete=models.SET_NULL
    )
    keywords = models.ManyToManyField(
        DKeyword, related_name="documents", db_table="document_keyword"
    )
    data_source = models.ForeignKey(
        DDataSource, blank=True, null=True, on_delete=models.SET_NULL
    )
    organization = models.ForeignKey(
        Organization, blank=True, null=True, on_delete=models.SET_NULL
    )
    published_year = models.IntegerField(blank=True, null=True)
    data_collection_start_year = models.IntegerField(blank=True, null=True)
    data_collection_end_year = models.IntegerField(blank=True, null=True)
    next_update_year = models.IntegerField(blank=True, null=True)
    nuts_levels = models.ManyToManyField(
        DNutsLevel, related_name="documents", db_table="document_nuts_level"
    )
    # TODO: Discuss dropping this, as terms here are conflated with keywords contents
    additional_info = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "document"

    def __str__(self):
        return self.title

    @property
    def download_url(self):
        return reverse(
            "search:document-download",
            kwargs={"pk": self.pk},
        )

    @classmethod
    def save_metadata_record(cls, rec, import_batch=None, import_file=True):

        doc_data = attr.asdict(rec)
        doc_data = {
            field: value
            for field, value in doc_data.items()
            if field in rec.relevant_fields()
        }

        # Prepare FK relations
        # Map dictionary relation name to a tuple of:
        # <related model>, (<related model field 1>, <corresponding metadata field 1>, ...)
        # The specified related model fields must be able to uniquely identify the related instance.
        fk_rels = {
            "data_type": (DDataType, (("name", "data_type"),)),
            "data_set": (DDataSet, (("name", "data_set"),)),
            "resource_type": (DResourceType, (("name", "resource_type"),)),
            "info_level": (DInfoLevel, (("name", "info_level"),)),
            "topic_category": (DTopicCategory, (("name", "topic_category"),)),
            "data_source": (DDataSource, (("name", "data_source"),)),
            "organization": (
                Organization,
                (("name", "organization"), ("email", "organization_email")),
            ),
        }

        for relation, details in fk_rels.items():
            model, field_pairs = details
            relation_filter = {p[0]: doc_data[p[1]] for p in field_pairs}
            if any(relation_filter.values()):
                try:
                    doc_data[relation] = model.objects.get(**relation_filter)
                except model.DoesNotExist:
                    print(
                        f"row={rec.id} {relation_filter} not found in {model.__name__}"
                    )
                    return None

            else:
                doc_data.pop(relation, None)

        # Remove non-Document fields (e.g. 'organization_email')
        discard_fields = [
            p[1]
            for v in fk_rels.values()
            for p in v[1]
            if p[1] not in fk_rels.keys()
        ]
        for f in discard_fields:
            doc_data.pop(f)

        # Pop off M2M raw data before creating doc (M2M needs id)
        countries = doc_data.pop("countries", [])
        countries = DCountry.objects.filter(name__in=countries)

        nuts_levels = doc_data.pop("nuts_levels", [])
        nuts_levels = DNutsLevel.objects.filter(name__in=nuts_levels)

        keywords = doc_data.pop("keywords", [])
        additional_info = doc_data.pop("additional_info", [])
        keywords = DKeyword.objects.filter(name__in=set(keywords + additional_info))

        location = doc_data.pop("resource_locator_internal2", None)
        external_link = doc_data.pop("resource_locator_external", None)
        languages = doc_data.pop("languages", [])
        geo_fields = (
            "bound_north",
            "bound_east",
            "bound_south",
            "bound_west",
            "projection",
            "spatial_resolution",
        )
        geo_bounds = {field: doc_data.pop(field, None) for field in geo_fields}

        doc_data["import_batch"] = import_batch
        doc_data["metadata_id"] = rec.id

        try:
            doc = Document.objects.create(**doc_data)
        except Exception:
            log.error(f"Could not create document with metadata: {doc_data}")
            raise

        # Add M2M relations
        doc.countries.set(countries)
        doc.nuts_levels.set(nuts_levels)
        doc.keywords.set(keywords)
        doc.save()

        # Create geo bounds if available
        if any(v for v in geo_bounds.values()):
            geo_bounds["document"] = doc
            GeographicBounds.objects.create(**geo_bounds)

        # Create file and associate languages
        if location is not None or external_link is not None:
            file = DocumentFile.objects.create(
                document=doc, original_path=location, external_link=external_link
            )
            if languages:
                languages = DLanguage.objects.filter(name__in=languages)
                file.languages.set(languages)
                file.save()
            # Only import file once per original metadata record
            if import_file and location is not None:
                file.import_file()

        return doc

    @classmethod
    def associate_records(cls, records, track_progress=False):
        """Set inter-document associations"""
        for rec in tqdm(records, desc="Associating records", disable=not track_progress):
            if rec.document is None:
                continue
            if rec.higher_level_ids:
                log.debug(f"Associating doc {rec.id} with higher level docs {rec.higher_level_ids}")
                higher_level_docs = Document.objects.filter(
                    import_batch=rec.document.import_batch,
                    metadata_id__in=rec.higher_level_ids
                )
                rec.document.higher_level_docs.set(higher_level_docs)
            if rec.same_level_ids:
                log.debug(f"Associating doc {rec.id} with same level docs {rec.same_level_ids}")
                same_level_docs = Document.objects.filter(
                    import_batch=rec.document.import_batch,
                    metadata_id__in=rec.same_level_ids
                )
                rec.document.same_level_docs.set(same_level_docs)
            if rec.lower_level_ids:
                log.debug(f"Associating doc {rec.id} with lower level docs {rec.lower_level_ids}")
                lower_level_docs = Document.objects.filter(
                    import_batch=rec.document.import_batch,
                    metadata_id__in=rec.lower_level_ids
                )
                rec.document.lower_level_docs.set(lower_level_docs)
            rec.document.save()

    @classmethod
    def save_metadata_records(cls, records, import_batch=None, import_files=True, track_progress=False):
        """Creates `Document`s from a list of `MetadataRecord`s"""
        for rec in tqdm(records, desc="Importing documents metadata", disable=not track_progress):
            rec.document = cls.save_metadata_record(
                rec,
                import_batch=import_batch,
                import_file=import_files,
            )
        cls.associate_records(records, track_progress)

    def populate_text(self, force=False):
        if self.text is None or force:
            if self.file is not None and self.file.path is not None:
                self.text = self.file.get_text()
                try:
                    self.save()
                except ESConnectionTimeout:
                    log.error(
                        f"ElasticSearch timeout while indexing text for document {self.pk}"
                    )

    @classmethod
    def collection_range(cls):
        return (
            cls.objects.all().aggregate(min=models.Min('data_collection_start_year'))['min'],
            cls.objects.all().aggregate(max=models.Max('data_collection_end_year'))['max']
        )

    @classmethod
    def publication_years(cls):
        return set(cls.objects.values_list('published_year', flat=True).order_by('published_year'))


class FileStorage(FileSystemStorage):
    def __init__(self):
        # Keep the explicit location out of migrations
        super().__init__(location=str(settings.FILES_DIR))


def get_upload_path(instance, file_name):
    return instance.get_upload_path(file_name)


class DocumentFile(models.Model):
    document = models.OneToOneField(
        Document, on_delete=models.CASCADE, related_name="file"
    )
    file = models.FileField(
        upload_to=get_upload_path,
        max_length=512,
        storage=FileStorage(),
        null=True,
        blank=True,
    )
    original_path = models.TextField(blank=True, null=True)
    external_link = models.TextField(blank=True, null=True)
    file_size = models.IntegerField(blank=True, null=True)
    file_type = models.ForeignKey(
        DFileType, blank=True, null=True, on_delete=models.SET_NULL
    )
    languages = models.ManyToManyField(
        DLanguage, related_name="files", db_table="document_file_language"
    )

    class Meta:
        db_table = "document_file"

    def __str__(self):
        return self.external_link

    @property
    def name(self):
        return os.path.basename(self.file.name)

    @property
    def extension(self):
        return self.name.split(".")[-1].lower()

    @property
    def size(self):
        return self.file.size

    @property
    def original_relative_path(self):
        """File path relative to the metadata path."""
        _path = None
        if self.original_path is not None and self.document.import_batch is not None:
            try:
                if self.document.import_batch.posix_original_path:
                    _path = PurePosixPath(self.original_path).relative_to(
                        self.document.import_batch.original_path_root
                    )
                else:
                    _path = PureWindowsPath(self.original_path).relative_to(
                        self.document.import_batch.original_path_root
                    )
            except ValueError:
                pass  # Fall through to None response when original path does not respect the prefix

        return _path

    def get_upload_path(self, file_name):
        """Returns the file path relative to storage location"""
        upload_path = Path(self.document.import_batch.path) / self.original_relative_path
        abs_upload_path = Path(self.file.storage.location) / upload_path
        abs_upload_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure path dirs exist
        return str(upload_path)

    def import_file(self):
        """Copies the file from the import directory to the files storage dir."""
        rel_path = self.original_relative_path
        if rel_path is None:
            log.error(
                f"Could not import file id={self.pk}: original path or prefix not found"
            )
            return

        file_name = rel_path.name

        src_path = Path(settings.IMPORT_FILES_DIR) / self.original_relative_path
        try:
            src_path = src_path.resolve(strict=True)
        except FileNotFoundError:
            log.error(f"Import file not found: {src_path}")
            return

        self.file.save(name=file_name, content=File(src_path.open(mode="rb")))
        print(f"Copied {src_path} to {self.file.path}")
        self.save()

    def get_text(self):
        """Sends the file to Tika and returns the extracted text."""
        try:
            path = Path(self.file.path).resolve(strict=True)
        except FileNotFoundError:
            log.error(f'Text extraction: file not found "{path}"')
            return

        with open(path, "rb") as f:
            try:
                return extract_text(f)

            except TextExtractionTimeout:
                log.error(f"Text extraction timed out on {f.name}")
            except TextExtractionError:
                log.error(f"Text extraction failed on {f.name}")

    def delete(self, *args, **kwargs):
        try:
            os.remove(self.file.path)
            debug(f'Deleted disk file {self.file.path}')
        except FileNotFoundError:
            error(
                f'Could not delete envelope file from disk (not found): '
                f'{self.file.path}'
            )

        super().delete(*args, **kwargs)


class GeographicBounds(models.Model):
    document = models.ForeignKey(
        Document,
        blank=True,
        null=True,
        related_name="geo_bounds",
        on_delete=models.CASCADE,
    )
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
        db_table = "geographic_bounds"
        verbose_name_plural = "GeographicBounds"

    def __str__(self):
        return "{} - N:{}, E:{}, S:{}, W:{}".format(
            self.document.title,
            self.bound_north,
            self.bound_east,
            self.bound_south,
            self.bound_west,
        )


class CountryData(models.Model):
    country = models.ForeignKey(
        "DCountry", blank=True, null=True, related_name="data", on_delete=models.CASCADE
    )
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
        db_table = "country_data"
        verbose_name_plural = "CountryData"


class GEMETConcept(models.Model):
    broader = models.ForeignKey(
        "self",
        related_name="narrower",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    related = models.ManyToManyField("self", blank=True)

    class Meta:
        db_table = "gemet_concept"

    @classmethod
    def translation_synonyms(cls):
        """
        Returns list of autophrased synonyms/translations, e.g.::

            deciduous_forest => floresta_caducifólia, pădure_de_foioase (, ...)

        """
        synonyms = []
        for concept in cls.objects.all():
            try:
                en = concept.names.get(language="en")
            except cls.DoesNotExist:
                continue
            en_syn = en.autophrased_name
            non_en = concept.names.filter(~models.Q(language="en")).all()
            if non_en:
                non_en_syns = ", ".join([o.autophrased_name for o in non_en.all()])
                synonyms.append(f"{en_syn} => {non_en_syns}")
        return synonyms

    @classmethod
    def autophrased_synonyms(cls):
        """
        Returns list of autophrasing synonyms, .e.g::

            deciduous_forest => deciduous forest

        """
        synonyms = []
        for concept in cls.objects.all():
            for name in concept.names.all():
                if name.clean_name != name.autophrased_name:
                    synonyms.append(f"{name.clean_name} => {name.autophrased_name}")

        return synonyms


class GEMETConceptLanguage(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=60)

    class Meta:
        db_table = "gemet_concept_language"


class GEMETConceptName(models.Model):
    concept = models.ForeignKey(
        GEMETConcept, related_name="names", on_delete=models.CASCADE
    )
    language = models.ForeignKey(GEMETConceptLanguage, on_delete=models.CASCADE)
    name = models.TextField()

    class Meta:
        db_table = "gemet_concept_name"
        unique_together = ("concept", "language")

    @property
    def clean_name(self):
        clean = self.name
        # Break off a first enumeration/detailing/formatting marker
        stops = [".", ",", ";", ":" "?", "!", "'", "(", "[", "{", "<", "\\", "/", "\n"]
        for m in stops:
            if m in clean:
                clean = clean[: clean.index(m)].strip()

        return clean.strip()

    @property
    def autophrased_name(self):
        return "_".join(self.clean_name.split(" "))
