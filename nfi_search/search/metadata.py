from itertools import count
from enum import IntEnum
import attr


NULL_SUROGATES = ('', 'N.A.', 'n.a.')


def strip_or_none(value):
    try:
        stripped = value.strip()
    except AttributeError:
        return None
    return stripped if stripped not in NULL_SUROGATES else None


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
    Splits `value` on commas and `and`s. Skips null surrogates.
    """
    if not isinstance(value, str):
        return []
    data = [
        strip_or_none(f)
        for e in value.split(',')
        for f in e.split(' and ')
    ]
    return [e for e in data if e is not None]


@attr.s
class MetadataRecord:
    id = attr.ib(converter=int_or_none, metadata={'mandatory': True})
    country = attr.ib(
        converter=strip_or_none,
        metadata={'dictionary_cls': 'DCountry', 'relevant': True, 'mandatory': True},
    )
    country_id = attr.ib(
        converter=int_or_none, metadata={'relevant': True, 'mandatory': True}
    )
    data_type = attr.ib(
        converter=strip_or_none, metadata={'dictionary_cls': 'DDataType', 'relevant': True}
    )
    data_set = attr.ib(
        converter=strip_or_none, metadata={'dictionary_cls': 'DDataSet', 'relevant': True}
    )
    resource_type = attr.ib(
        converter=strip_or_none, metadata={'dictionary_cls': 'DResourceType', 'relevant': True}
    )
    info_level = attr.ib(
        converter=strip_or_none, metadata={'dictionary_cls': 'DInfoLevel', 'relevant': True}
    )
    topic_category = attr.ib(
        converter=strip_or_none, metadata={'dictionary_cls': 'DTopicCategory', 'relevant': True}
    )
    data_source = attr.ib(
        converter=strip_or_none, metadata={'dictionary_cls': 'DDataSource', 'relevant': True}
    )
    link_to_parent = attr.ib(converter=strip_or_none)
    parent_id = attr.ib(converter=int_or_none)
    sibling_ids = attr.ib(converter=int_or_none)
    children_ids = attr.ib(converter=int_or_none)
    resource_locator_internal = attr.ib(converter=strip_or_none, metadata={'relevant': True})
    resource_locator_internal2 = attr.ib(converter=strip_or_none)
    resource_locator_external = attr.ib(converter=strip_or_none, metadata={'relevant': True})
    organization = attr.ib(
        converter=strip_or_none, metadata={'dictionary_cls': 'Organization', 'relevant': True}
    )
    organization_email = attr.ib(converter=strip_or_none, metadata={'relevant': True})
    title = attr.ib(converter=strip_or_none, metadata={'relevant': True})
    description = attr.ib(converter=strip_or_none, metadata={'relevant': True})
    languages = attr.ib(
        converter=comma_string_to_list,
        metadata={'dictionary_cls': 'DLanguage', 'relevant': True},
    )
    published_year = attr.ib(converter=int_or_none, metadata={'relevant': True})
    data_collection_start_year = attr.ib(
        converter=int_or_none, metadata={'relevant': True}
    )
    data_collection_end_year = attr.ib(
        converter=int_or_none, metadata={'relevant': True}
    )
    next_update_year = attr.ib(converter=int_or_none, metadata={'relevant': True})
    nuts_levels = attr.ib(
        converter=comma_string_to_list,
        metadata={'dictionary_cls': 'DNutsLevel', 'relevant': True},
    )
    forest_ownership_ha = attr.ib()
    forest_types_ha = attr.ib()
    tree_species_ha = attr.ib()
    age_classes_ha = attr.ib()
    diameter_dbh = attr.ib()
    quality_indicators_ha = attr.ib()
    forest_management_ha = attr.ib()
    afforestation_ha = attr.ib()
    felling_ha = attr.ib()
    additional_info = attr.ib(converter=comma_string_to_list, metadata={'relevant': True})
    keywords = attr.ib(
        converter=comma_string_to_list,
        metadata={'dictionary_cls': 'DKeyword', 'relevant': True},
    )
    metadata = attr.ib()
    metadata_location = attr.ib()
    bound_north = attr.ib(converter=float_or_none, metadata={'relevant': True})
    bound_east = attr.ib(converter=float_or_none, metadata={'relevant': True})
    bound_south = attr.ib(converter=float_or_none, metadata={'relevant': True})
    bound_west = attr.ib(converter=float_or_none, metadata={'relevant': True})
    projection = attr.ib(converter=strip_or_none, metadata={'relevant': True})
    spatial_resolution = attr.ib(converter=strip_or_none, metadata={'relevant': True})
    file_size = attr.ib()
    to_transfer_set_no = attr.ib()
    added_until_date = attr.ib()

    @classmethod
    def relevant_fields(cls):
        return [field.name for field in attr.fields(cls) if field.metadata.get('relevant', False)]

    def is_valid(self):
        """
        Validates the record if all fields that have `metadata['mandatory']` set to `True` are non-empty.
        """
        # TODO: Decide what else should be required
        return all(
            [
                getattr(self, field.name) is not None
                for field in attr.fields(self.__class__)
                if field.metadata.get('mandatory', False)
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
            getattr(r, rec_field_name)
            for r in records
            if getattr(r, rec_field_name) is not None
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
