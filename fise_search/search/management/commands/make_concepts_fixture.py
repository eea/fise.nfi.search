from pathlib import Path
import requests
from rdflib import Graph
from urllib.parse import urldefrag
import csv
import yaml
from django.core.management.base import BaseCommand


# Languages supported by GEMET except Chinese,
# which has errors in its definitions RDF)
LANGUAGES = (
    'ar',
    'hy',
    'az',
    'eu',
    'bg',
    'ca',
    'hr',
    'cs',
    'da',
    'nl',
    'en',
    'et',
    'fi',
    'fr',
    'ka',
    'de',
    'el',
    'hu',
    'is',
    'ga',
    'it',
    'lv',
    'lt',
    'mt',
    'no',
    'pl',
    'pt',
    'ro',
    'ru',
    'sk',
    'sl',
    'es',
    'sv',
    'tr',
    'uk',
)


GEMET_DATA_DIR = Path('../data/gemet')
GEMET_FIXTURE_PATH = Path('../data/fixtures/concepts.yaml')

BACKBONE_URL = 'http://www.eionet.europa.eu/gemet/exports/latest/gemet-backbone.rdf'
RELATIONS_URL = 'http://www.eionet.europa.eu/gemet/exports/latest/gemet-skoscore.rdf'
DEFINITIONS_URL_TEMPLATE = 'http://www.eionet.europa.eu/gemet/exports/latest/{}/gemet-definitions.rdf'

CONCEPTS_GEMET_PREFIX = 'http://www.eionet.europa.eu/gemet/concept'
CONCEPTS_PREFIX = 'http://www.eionet.europa.eu/concept'
THEMES_NS = 'http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#theme'
THEMES_PREFIX = 'http://www.eionet.europa.eu/gemet/theme'
FORESTRY_THEME_ID = 14
SEMANTIC_RELATIONS = ('broader', 'narrower', 'related')


def download_file(url, path):
    print(f'Downloading {url} to {path}')
    r = requests.get(url, stream=True)
    with open(path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def get_element_id(url, required_prefix=None):
    prefix, _, element_id = url.rpartition('/')
    if required_prefix is None or prefix == required_prefix:
        try:
            return int(element_id)

        except ValueError:
            return None

    return None


def get_relation_type(url):
    return urldefrag(url)[1] or None


class AutoVivificatingDict(dict):

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)

        except KeyError:
            value = self[item] = type(self)()
            return value


class Command(BaseCommand):

    help = 'Create the fixture for GEMET forestry concepts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--download', action='store_true', help='Download RDFs from GEMET'
        )
        parser.add_argument(
            '--data-dir', default='data', help='Location of project' 's data directory'
        )

    def handle(self, *args, **options):
        self.data_dir = Path(options['data_dir']).resolve()
        if options['download']:
            self.download_backbone()
            self.download_relations()
            self.download_definitions()

        concepts = self.load_concepts()
        self.make_fixture(concepts)

    def download_backbone(self):
        download_file(BACKBONE_URL, self.data_dir / 'gemet' / 'gemet-backbone.rdf')

    def download_relations(self):
        download_file(RELATIONS_URL, self.data_dir / 'gemet' / 'gemet-skoscore.rdf')

    def download_definitions(self):
        for lang in LANGUAGES:
            download_file(
                DEFINITIONS_URL_TEMPLATE.format(lang),
                self.data_dir / 'gemet' / f'{lang}-gemet-definitions.rdf',
            )

    def load_concepts(self):
        backbone_path = self.data_dir / 'gemet' / 'gemet-backbone.rdf'
        backbone_graph = Graph()
        self.stdout.write(f'Loading backbone from {backbone_path} ...')
        with open(backbone_path) as f:
            backbone_graph.parse(f)

        forestry_concepts = set()
        # Filter forestry theme concepts from the backbone
        for sub, pred, obj in backbone_graph.triples((None, None, None)):
            concept_id = get_element_id(sub, CONCEPTS_GEMET_PREFIX)
            is_theme_assignment = str(pred) == THEMES_NS
            theme_id = get_element_id(obj, THEMES_PREFIX)
            if is_theme_assignment and theme_id == FORESTRY_THEME_ID and concept_id is not None:
                forestry_concepts.add(concept_id)

        concepts = AutoVivificatingDict()

        relations_path = self.data_dir / 'gemet' / 'gemet-skoscore.rdf'
        self.stdout.write(f'Loading relations from {relations_path} ...')
        relations_graph = Graph()
        with open(relations_path) as f:
            relations_graph.parse(f)

        for concept, relation, target_concept in relations_graph.triples(
            (None, None, None)
        ):
            concept_id = get_element_id(concept, CONCEPTS_GEMET_PREFIX)
            target_concept_id = get_element_id(target_concept, CONCEPTS_GEMET_PREFIX)
            if concept_id in forestry_concepts and target_concept_id in forestry_concepts:
                relation_type = get_relation_type(relation)
                if relation_type == 'broader':
                    concepts[target_concept_id]['broader'] = concept_id
                elif relation_type == 'narrower':
                    concepts[concept_id]['broader'] = target_concept_id
                elif relation_type == 'related':
                    if 'relations' not in concepts[concept_id]:
                        concepts[concept_id]['related'] = [target_concept_id]
                    else:
                        concepts[concept_id]['related'].append(target_concept_id)

        for lang in LANGUAGES:
            definitions_path = self.data_dir / 'gemet' / f'{lang}-gemet-definitions.rdf'
            self.stdout.write(
                f'Loading "{lang}" definitions from {definitions_path} ...'
            )
            definitions_graph = Graph()
            with open(definitions_path) as f:
                definitions_graph.parse(f)

            for concept in definitions_graph.subjects():
                concept_id = get_element_id(concept, CONCEPTS_PREFIX)
                if concept_id in forestry_concepts:
                    name = str(
                        definitions_graph.preferredLabel(concept, lang=lang)[0][1]
                    )
                    if 'names' not in concepts[concept_id]:
                        concepts[concept_id]['names'] = {lang: name}
                    else:
                        concepts[concept_id]['names'][lang] = name

        return concepts

    def make_fixture(self, concepts):

        fixture_data = []

        # Language fixtures (GEMET-used only)
        with open(self.data_dir / 'languages.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] in LANGUAGES:
                    fixture_data.append(
                        {
                            'model': 'search.gemetconceptlanguage',
                            'pk': row[0],
                            'fields': {'name': row[1]},
                        }
                    )

        # Concept and concept name fixtures
        for concept_id, concept in concepts.items():
            concept_fields = {}
            if 'broader' in concept:
                concept_fields['broader'] = concept['broader']
            if 'related' in concept:
                concept_fields['related'] = concept['related']

            concept_fixture = {
                'model': 'search.gemetconcept',
                'pk': concept_id,
                'fields': concept_fields,
            }

            fixture_data.append(concept_fixture)

            for lang, name in concept['names'].items():
                fixture_data.append(
                    {
                        'model': 'search.gemetconceptname',
                        'fields': {
                            'concept': concept_id, 'language': lang, 'name': name
                        },
                    }
                )

        fixture_path = self.data_dir / 'fixtures' / 'gemet_concepts.yaml'
        self.stdout.write(f'Dumping concepts to fixture {fixture_path}')
        with open(fixture_path, 'w') as f:
            yaml.dump(fixture_data, f)
