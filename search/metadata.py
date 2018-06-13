from itertools import count
from enum import IntEnum
import attr


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
    country = attr.ib(metadata={'dictionary_cls': 'DCountry'})
    country_id = attr.ib(converter=int_or_none)
    data_type = attr.ib(metadata={'dictionary_cls': 'DDataType'})
    data_set = attr.ib(metadata={'dictionary_cls': 'DDataSet'})
    resource_type = attr.ib(metadata={'dictionary_cls': 'DResourceType'})
    info_level = attr.ib(metadata={'dictionary_cls': 'DInfoLevel'})
    topic_category = attr.ib(metadata={'dictionary_cls': 'DTopicCategory'})
    data_source = attr.ib(metadata={'dictionary_cls': 'DDataSource'})
    link_to_higher_information_level = attr.ib()
    parent_id = attr.ib(converter=int_or_none)
    sibling_ids = attr.ib(converter=int_or_none)
    children_ids = attr.ib(converter=int_or_none)
    resource_locator_internal = attr.ib()
    resource_locator_internal2 = attr.ib()
    resource_locator_external = attr.ib()
    responsible_organization = attr.ib(metadata={'dictionary_cls': 'Organization'})
    organization_email = attr.ib()
    resource_title = attr.ib()
    resource_description = attr.ib()
    languages = attr.ib(converter=comma_string_to_list, metadata={'dictionary_cls': 'DLanguage'})
    published_year = attr.ib(converter=int_or_none)
    data_collection_start_year = attr.ib(converter=int_or_none)
    data_collection_end_year = attr.ib(converter=int_or_none)
    next_update_year = attr.ib(converter=int_or_none)
    nuts_levels = attr.ib(converter=comma_string_to_list, metadata={'dictionary_cls': 'DNutsLevel'})
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
    keywords = attr.ib(converter=comma_string_to_list, metadata={'dictionary_cls': 'DKeyword'})
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

    relevant_fields = (
        'country',
        'country_id',
        'data_type',
        'data_set',
        'resource_type',
        'info_level',
        'topic_category',
        'data_source',
        # 'organization_email',
        # 'responsible_organization',
        'published_year',
        'data_collection_start_year',
        'data_collection_end_year',
        'next_update_year',
        'nuts_levels',
        'additional_info',
        'keywords',
        # 'geographic_bounding_box_north',
        # 'geographic_bounding_box_east',
        # 'geographic_bounding_box_south',
        # 'geographic_bounding_box_west',
        # 'projection',
        # 'spatial_resolution',
    )

    # Mandatory fields must be non-empty for the record to be valid
    # TODO: Decide what else should be required
    mandatory_fields = ('id', 'country', 'country_id')

    def is_valid(self):
        return all(
            [
                getattr(self, field_name) is not None
                for field_name in self.mandatory_fields
            ]
        )


# noinspection PyTypeChecker
MetadataColumns = IntEnum(
    'Columns', zip([f.name for f in attr.fields(MetadataRecord)], count())
)


def prepare_data(model, target_field_name, rec_field_name, records):
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
        # for o in model.objects.filter(**filter_clause)
    ]
    data = [d for d in data if d not in existing]
    return data


def update_data(model, field_name, data):
    """
    Bulk-inserts `data` into `model`'s field `field_name`
    Returns:
        The number of objects inserted.
    """
    orig_count = model.objects.count()
    objs = [model(**{field_name: d}) for d in data]
    model.objects.bulk_create(objs, batch_size=100)
    return model.objects.count() - orig_count
