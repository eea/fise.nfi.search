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
    return [e.strip() for e in value.split(',') if e.strip()]


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
    responsible_organisation = attr.ib()
    organisation_email = attr.ib()
    resource_title = attr.ib()
    resource_description = attr.ib()
    language = attr.ib()
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
    additional_info = attr.ib()
    keywords = attr.ib()
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


def _update_data(model, target_field_name, rec_field_name, records):
    data = set([getattr(r, rec_field_name).strip() for r in records if getattr(r, rec_field_name).strip()])
    filter_clause = {f'{target_field_name}__in': data}
    existing = [
        getattr(o, target_field_name) for o in model.objects.only(target_field_name).filter(**filter_clause)
    ]
    data = [d for d in data if d not in existing]
    orig_count = model.objects.count()
    objs = [model(**{target_field_name: d}) for d in data]
    model.objects.bulk_create(objs, batch_size=100)
    return model.objects.count() - orig_count


def update_data_types(records):
    return _update_data(DDataType, 'name', 'data_type', records)


def update_data_sets(records):
    return _update_data(DDataSet, 'name', 'data_set', records)


def update_resource_types(records):
    return _update_data(DResourceType, 'name', 'resource_type', records)


def update_info_levels(records):
    return _update_data(DInfoLevel, 'name', 'resource_type', records)


def update_topic_categories(records):
    return _update_data(DTopicCategory, 'name', 'topic_category', records)


def update_data_sources(records):
    return _update_data(DDataSource, 'name', 'data_source', records)


def update_nuts_levels(records):
    data = set([level for r in records for level in r.nuts_levels])
    existing = [
        DNutsLevel.name for o in DNutsLevel.objects.only('name').filter(name__in=data)
    ]
    data = [d for d in data if d not in existing]
    orig_count = DNutsLevel.objects.count()
    objs = [DNutsLevel(name=d) for d in data]
    DNutsLevel.objects.bulk_create(objs, batch_size=100)
    return DNutsLevel.objects.count() - orig_count
