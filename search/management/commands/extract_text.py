from django.core.management.base import BaseCommand
from search.models import Document


class Command(BaseCommand):

    help = 'Extract text from documents'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--force-refresh', type=bool, default=False)

    def handle(self, *args, **options):
        force = options['force_refresh']
        for d in Document.objects.filter(file__isnull=False, file__location__isnull=False):
            self.stdout.write(f'Extracting text from {d.file.get_relative_path()} ... ')
            self.stdout.flush()
            d.populate_text(force=force)
