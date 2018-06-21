from pprint import pprint
from collections import defaultdict
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, SKOS
from rdflib.term import URIRef, Literal
from urllib.parse import urldefrag

CONCEPTS_GEMET_PREFIX = 'http://www.eionet.europa.eu/gemet/concept'
CONCEPTS_PREFIX = 'http://www.eionet.europa.eu/concept'
THEMES_NS = 'http://www.eionet.europa.eu/gemet/2004/06/gemet-schema.rdf#theme'
THEMES_PREFIX = 'http://www.eionet.europa.eu/gemet/theme'
FORESTRY_THEME_ID = 14

BACKBONE_FILE = '/Users/andrei/Desktop/gemet-backbone.rdf'
DEFINITIONS_FILES = {
    'en': '/Users/andrei/Desktop/gemet-definitions.rdf'
}
RELATIONS_FILE = '/Users/andrei/Desktop/gemet-skoscore.rdf'

SEMANTIC_RELATIONS = (
    'broader',
    'narrower',
    'related',
)


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


class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


def main():

    backbone_graph = Graph()
    print(f'Loading backbone from {BACKBONE_FILE} ...')
    with open(BACKBONE_FILE) as f:
        backbone_graph.parse(f)

    forestry_concepts = set()

    for sub, pred, obj in backbone_graph.triples((None, None, None)):
        concept_id = get_element_id(sub, CONCEPTS_GEMET_PREFIX)
        is_theme_assignment = str(pred) == THEMES_NS
        theme_id = get_element_id(obj, THEMES_PREFIX)
        if is_theme_assignment and theme_id == FORESTRY_THEME_ID and concept_id is not None:
            forestry_concepts.add(concept_id)

    # print(forestry_concepts)

    # concepts = defaultdict(dict)
    concepts = AutoVivification()

    for lang, defs_file in DEFINITIONS_FILES.items():
        print(f'Loading "{lang}" definitions from {defs_file} ...')
        definitions_graph = Graph()
        with open(defs_file) as f:
            definitions_graph.parse(f)

        for concept in definitions_graph.subjects():
            concept_id = get_element_id(concept, CONCEPTS_PREFIX)
            if concept_id in forestry_concepts:
                label = str(definitions_graph.preferredLabel(concept, lang=lang)[0][1])
                if 'label' not in concepts[concept_id]:
                    concepts[concept_id]['labels'] = {lang: label}
                else:
                    concepts[concept_id]['labels'][lang] = label

    # pprint(concepts)

    relations_graph = Graph()
    print('Loading relations ...')
    with open(RELATIONS_FILE) as f:
        relations_graph.parse(f)

    for concept, relation, target_concept in relations_graph.triples((None, None, None)):
        concept_id = get_element_id(concept, CONCEPTS_GEMET_PREFIX)
        relation_type = get_relation_type(relation)
        target_concept_id = get_element_id(target_concept, CONCEPTS_GEMET_PREFIX)
        # print(concept_id, relation_type, target_concept_id)
        if concept_id in forestry_concepts and target_concept_id in forestry_concepts:
            if relation_type == 'broader':
                concepts[target_concept_id]['parent'] = concept_id
            elif relation_type == 'narrower':
                concepts[concept_id]['parent'] = target_concept_id
            elif relation_type == 'related':
                if 'relations' not in concepts[concept_id]:
                    concepts[concept_id]['relations'] = [target_concept_id]
                else:
                    concepts[concept_id]['relations'].append(target_concept_id)
        # elif relation_type in SEMANTIC_RELATIONS:
        #     print(concept_id, target_concept_id)

    pprint(concepts)


if __name__ == '__main__':
    main()

