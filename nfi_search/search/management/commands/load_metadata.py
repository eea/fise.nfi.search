from django.core.management.base import BaseCommand
from django.apps import apps
import defusedxml
import attr
from xlrd import open_workbook

from ...metadata import MetadataRecord, MetadataColumns

from ...models import Document, DocumentImportBatch

defusedxml.defuse_stdlib()


class Command(BaseCommand):
    help = "Load NFI metadata"

    def add_arguments(self, parser):
        parser.add_argument("file")
        parser.add_argument("-i", "--ignore-errors", type=bool, default=False)
        parser.add_argument("-f", "--import-files", type=bool, default=True)
        parser.add_argument("-r", "--original-path-root", type=str)
        parser.add_argument("-p", "--posix-original-path", type=bool, default=False)
        parser.add_argument("-b", "--progress-bar", type=bool, default=False)
        parser.add_argument("--country")
        parser.add_argument("--data-type")
        parser.add_argument("--data-set")
        parser.add_argument("--resource-type")
        parser.add_argument("--info-level")
        parser.add_argument("--topic-category")

    def update_dictionaries(self, records):
        self.stdout.write("Updating dictionaries ...")
        dictionary_fields = [
            f for f in attr.fields(MetadataRecord) if "dictionary_cls" in f.metadata
        ]

        for field in dictionary_fields:
            model = apps.get_model("search", field.metadata["dictionary_cls"])
            self.stdout.write(f"  {field.name: <30} ", ending="")
            new = model.update_from_metadata(records)
            if new > 0:
                self.stdout.write(f"{new: >8} added.")
            else:
                self.stdout.write("{0: >15}".format("no new values."))

    def handle(self, *args, **options):
        ignore_errors = options["ignore_errors"]
        import_files = options["import_files"]
        original_path_root = options["original_path_root"]
        posix_original_path = options["posix_original_path"]
        progress_bar = options["progress_bar"]
        country = options["country"].upper()
        data_type = options["data_type"].upper()
        data_set = options["data_set"].upper()
        resource_type = options["resource_type"].upper()
        info_level = options["info_level"].upper()
        topic_category = options["topic_category"].upper()

        import_batch = DocumentImportBatch.objects.create(
            original_path_root=original_path_root,
            posix_original_path=posix_original_path,
        )
        try:
            with open_workbook(options["file"], on_demand=True) as book:
                sheet = book.sheet_by_index(0)
                records = []
                for rowno in range(1, sheet.nrows):
                    data = {
                        field.name: sheet.cell_value(rowno, MetadataColumns[field.name])
                        for field in attr.fields(MetadataRecord)
                    }
                    rec = MetadataRecord(**data)
                    if rec.is_valid():
                        if country and country not in [c.upper() for c in rec.countries]:
                            continue
                        elif data_type and rec.data_type.upper() != data_type:
                            continue
                        elif data_set and rec.data_set.upper() != data_set:
                            continue
                        elif resource_type and rec.resource_type.upper() != resource_type:
                            continue
                        elif info_level and rec.info_level.upper() != info_level:
                            continue
                        elif topic_category and rec.topic_category.upper != topic_category:
                            continue

                        records.append(rec)

                    elif not ignore_errors:
                        break

                self.update_dictionaries(records)
                Document.save_metadata_records(
                    records,
                    import_batch=import_batch,
                    import_files=import_files,
                    track_progress=progress_bar
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Processed {len(records)} rows from sheet "{sheet.name}"'
                    )
                )
        # Disallow XML with <!ENTITY> declarations inside the DTD
        # (https://github.com/python-excel/xlrd/issues/173)
        except defusedxml.EntitiesForbidden:
            self.stdout.write(self.style.ERROR("Please use a xlsx file without XEE"))
