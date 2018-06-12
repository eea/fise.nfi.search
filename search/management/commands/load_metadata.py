from django.core.management.base import BaseCommand
import defusedxml
import attr
from xlrd import open_workbook

from ._metadata import (
    MetadataRecord,
    MetadataColumns,
    update_countries,
    update_data_types,
    update_data_sets,
    update_resource_types,
    update_info_levels,
    update_topic_categories,
    update_data_sources,
    update_nuts_levels,
    update_keywords,
    update_languages,
    update_organizations,
    update_file_types,
)

defusedxml.defuse_stdlib()


class Command(BaseCommand):

    help = 'Load NFI metadata'

    def add_arguments(self, parser):
        parser.add_argument('file')
        parser.add_argument('-s', '--startrow', type=int, default=1)
        parser.add_argument('-e', '--endrow', type=int)

    def update_dictionaries(self, records):
        new = update_countries(records)
        if new > 0:
            self.stdout.write(f'Added {new} countries')

        new = update_data_types(records)
        if new > 0:
            self.stdout.write(f'Added {new} data types')

        new = update_data_sets(records)
        if new > 0:
            self.stdout.write(f'Added {new} data sets')

        new = update_resource_types(records)
        if new > 0:
            self.stdout.write(f'Added {new} resource types')

        new = update_info_levels(records)
        if new > 0:
            self.stdout.write(f'Added {new} info levels')

        new = update_topic_categories(records)
        if new > 0:
            self.stdout.write(f'Added {new} topic categories')

        new = update_data_sources(records)
        if new > 0:
            self.stdout.write(f'Added {new} data sources')

        new = update_nuts_levels(records)
        if new > 0:
            self.stdout.write(f'Added {new} NUTS levels')

        new = update_keywords(records)
        if new > 0:
            self.stdout.write(f'Added {new} keywords')

        new = update_languages(records)
        if new > 0:
            self.stdout.write(f'Added {new} languages')

        new = update_organizations(records)
        if new > 0:
            self.stdout.write(f'Added {new} organizations')

        new = update_file_types(records)
        if new > 0:
            self.stdout.write(f'Added {new} file types')

    def handle(self, *args, **options):
        start_row = options['startrow']
        try:
            with open_workbook(options['file'], on_demand=True) as book:
                sheet = book.sheet_by_index(0)
                end_row = options['endrow'] or sheet.nrows
                records = []
                for rowno in range(start_row, end_row):
                    data = {
                        field.name: sheet.cell_value(rowno, MetadataColumns[field.name])
                        for field in attr.fields(MetadataRecord)
                    }
                    records.append(MetadataRecord(**data))

                self.update_dictionaries(records)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Processed {len(records)} rows from sheet "{sheet.name}"'
                    )
                )
        except defusedxml.EntitiesForbidden:
            self.stdout.write(self.style.ERROR('Please use a xlsx file without XEE'))
