from django.core.management.base import BaseCommand
from django.apps import apps
import defusedxml
import attr
from xlrd import open_workbook

from search.metadata import (
    MetadataRecord,
    MetadataColumns,
)

from search.models import Document


defusedxml.defuse_stdlib()


class Command(BaseCommand):

    help = 'Load NFI metadata'

    def add_arguments(self, parser):
        parser.add_argument('file')
        parser.add_argument('-s', '--startrow', type=int, default=1)
        parser.add_argument('-e', '--endrow', type=int)
        parser.add_argument('-i', '--ignore-errors', type=bool, default=False)

    def update_dictionaries(self, records):
        self.stdout.write('Updating dictionaries ...')
        dictionary_fields = [
            f for f in attr.fields(MetadataRecord)
            if 'dictionary_cls' in f.metadata
        ]

        for field in dictionary_fields:
            model = apps.get_model('search', field.metadata['dictionary_cls'])
            self.stdout.write(f'  {field.name: <30} ', ending='')
            new = model.update_from_metadata(records)
            if new > 0:
                self.stdout.write(f'{new: >8} added.')
            else:
                self.stdout.write('{0: >15}'.format('no new values.'))

    def handle(self, *args, **options):
        start_row = options['startrow']
        ignore_errors = options['ignore_errors']
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
                    rec = MetadataRecord(**data)
                    if rec.is_valid():
                        records.append(rec)
                    elif not ignore_errors:
                        break

                self.update_dictionaries(records)
                self.stdout.write('Importing metadata records ... ')
                Document.save_metadata_records(records)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Processed {len(records)} rows from sheet "{sheet.name}"'
                    )
                )
        # Disallow XML with <!ENTITY> declarations inside the DTD
        # (https://github.com/python-excel/xlrd/issues/173)
        except defusedxml.EntitiesForbidden:
            self.stdout.write(self.style.ERROR('Please use a xlsx file without XEE'))
