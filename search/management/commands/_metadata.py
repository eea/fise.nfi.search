from itertools import count
from enum import IntEnum
import attr

from search.models import (
    DCountry,
    DDataType,
    DDataSet,
    DResourceType,
    DInfoLevel,
    DTopicCategory,
    DDataSource,
    DNutsLevel,
    DKeyword,
    DLanguage,
    Organization,
    DFileType,
)


def int_or_none(value):
    try:
        return int(value)

    except ValueError:
        return None


def float_or_none(value):
    try:
        return float(value)

    except ValueError:
        return None


def comma_string_to_list(value):
    """
    Splits `value` on commas and `and`s.
    """
    data = [e.strip() for e in value.split(',') if e.strip()]
    return [e.strip() for tok in data for e in tok.split(' and ') if e.strip()]


@attr.s
class MetadataRecord:
    id = attr.ib(converter=int_or_none)
    country = attr.ib()
    country_id = attr.ib(converter=int_or_none)
    data_type = attr.ib()
    data_set = attr.ib()
    resource_type = attr.ib()
    info_level = attr.ib()
    topic_category = attr.ib()
    data_source = attr.ib()
    link_to_higher_information_level = attr.ib()
    id_of_higher_information_level = attr.ib(converter=int_or_none)
    id_of_other_info_at_same_level = attr.ib(converter=int_or_none)
    id_of_lower_information_level = attr.ib(converter=int_or_none)
    resource_locator_internal = attr.ib()
    resource_locator_internal2 = attr.ib()
    resource_locator_external = attr.ib()
    responsible_organization = attr.ib()
    organization_email = attr.ib()
    resource_title = attr.ib()
    resource_description = attr.ib()
    languages = attr.ib(converter=comma_string_to_list)
    year_published = attr.ib(converter=int_or_none)
    year_data_collection_start = attr.ib(converter=int_or_none)
    year_data_collection_end = attr.ib(converter=int_or_none)
    year_next_update = attr.ib(converter=int_or_none)
    nuts_levels = attr.ib(converter=comma_string_to_list)
    forest_ownership_ha = attr.ib()
    forest_types_ha = attr.ib()
    tree_species_ha = attr.ib()
    age_classes_ha = attr.ib()
    diameter_dbh = attr.ib()
    quality_indicators_ha = attr.ib()
    forest_management_ha = attr.ib()
    afforestation_ha = attr.ib()
    felling_ha = attr.ib()
    additional_info = attr.ib(converter=comma_string_to_list)
    keywords = attr.ib(converter=comma_string_to_list)
    metadata = attr.ib()
    metadata_location = attr.ib()
    geographic_bounding_box_north = attr.ib(converter=float_or_none)
    geographic_bounding_box_east = attr.ib(converter=float_or_none)
    geographic_bounding_box_south = attr.ib(converter=float_or_none)
    geographic_bounding_box_west = attr.ib(converter=float_or_none)
    projection = attr.ib()
    spatial_resolution = attr.ib()
    file_size = attr.ib()
    to_transfer_set_no = attr.ib()
    added_until_date = attr.ib()


# noinspection PyTypeChecker
MetadataColumns = IntEnum(
    'Columns', zip([f.name for f in attr.fields(MetadataRecord)], count())
)


def update_countries(records):
    """Countries are a peculiar import case, as they come with ids in the metadata files."""
    countries = {
        r.country_id: r.country.strip()
        for r in records
        if r.country_id and r.country.strip()
    }
    existing = DCountry.objects.filter(id__in=countries.keys())
    for c in existing:
        countries.pop(c.pk, None)

    orig_count = DCountry.objects.count()
    objs = [DCountry(id=id, name=name) for id, name in countries.items()]
    DCountry.objects.bulk_create(objs, batch_size=100)
    return DCountry.objects.count() - orig_count


def _prepare_data(model, target_field_name, rec_field_name, records):
    """Prepares a list of unique, non-existing field values from a list of `MetadataRecords`"""
    data = set(
        [
            getattr(r, rec_field_name).strip()
            for r in records
            if getattr(r, rec_field_name).strip()
        ]
    )
    filter_clause = {f'{target_field_name}__in': data}
    existing = [
        getattr(o, target_field_name)
        for o in model.objects.only(target_field_name).filter(**filter_clause)
    ]
    data = [d for d in data if d not in existing]
    return data


def _update_data(model, field_name, data):
    """
    Bulk-inserts `data` into `model`'s field `field_name`
    Returns:
        The number of objects inserted.
    """
    orig_count = model.objects.count()
    objs = [model(**{field_name: d}) for d in data]
    model.objects.bulk_create(objs, batch_size=100)
    return model.objects.count() - orig_count


def update_data_types(records):
    data = _prepare_data(DDataType, 'name', 'data_type', records)
    return _update_data(DDataType, 'name', data)


def update_data_sets(records):
    data = _prepare_data(DDataSet, 'name', 'data_set', records)
    return _update_data(DDataSet, 'name', data)


def update_resource_types(records):
    data = _prepare_data(DResourceType, 'name', 'resource_type', records)
    return _update_data(DResourceType, 'name', data)


def update_info_levels(records):
    data = _prepare_data(DInfoLevel, 'name', 'info_level', records)
    return _update_data(DInfoLevel, 'name', data)


def update_topic_categories(records):
    data = _prepare_data(DTopicCategory, 'name', 'topic_category', records)
    return _update_data(DTopicCategory, 'name', data)


def update_data_sources(records):
    data = _prepare_data(DDataSource, 'name', 'data_source', records)
    return _update_data(DDataSource, 'name', data)


def update_nuts_levels(records):
    data = set([level for r in records for level in r.nuts_levels])
    existing = [o.name for o in DNutsLevel.objects.only('name').filter(name__in=data)]
    data = [d for d in data if d not in existing]
    return _update_data(DNutsLevel, 'name', data)


def update_keywords(records):
    """
    The keyword-specific columns are ignored, and keywords are extracted
    from the concatenated keyword columns ('KEYWORDS' and 'ADDITIONAL_INFO').
    """
    data = set(
        [w for r in records for w in r.keywords] +
        [w for r in records for w in r.additional_info]
    )

    existing = [o.name for o in DKeyword.objects.only('name').filter(name__in=data)]
    data = [d for d in data if d not in existing]
    return _update_data(DKeyword, 'name', data)


def update_languages(records):
    data = set([lang for r in records for lang in r.languages])
    existing = [o.name for o in DLanguage.objects.only('name').filter(name__in=data)]
    data = [d for d in data if d not in existing]
    return _update_data(DLanguage, 'name', data)


def update_organizations(records):
    # Organization.responsible_person is not populated, as the Excel data
    # seems to include that in the email column, with no consistent format.
    orgs = set(
        [
            (r.responsible_organization.strip(), r.organization_email.strip())
            for r in records
            if r.responsible_organization.strip()
        ]
    )

    new = 0
    for o in orgs:
        if not Organization.objects.filter(name=o[0], email=o[1]).exists():
            Organization.objects.create(name=o[0], email=o[1])
            new += 1
    return new


def update_file_types(records):
    data = set()
    for r in records:
        ext = r.resource_locator_internal.split('.')[-1].strip().lower()
        if ext:
            data.add(ext)

    existing = [o.name for o in DFileType.objects.only('name').filter(name__in=data)]
    data = [d for d in data if d not in existing]
    return _update_data(DFileType, 'name', data)
