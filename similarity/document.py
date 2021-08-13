import os
import yaml
import re

ITERATING_THRESHOLD = 10000


class DocumentCreator:

    @staticmethod
    def create(contribution_id, neo4j, is_query=False):
        """
        creates a document for a contribution_id
        """
        contribution_subgraph = neo4j._Neo4J__get_subgraph(contribution_id, bfs=True, with_ordering=False)

        if not contribution_subgraph:
            return None

        paths = build_paths(contribution_subgraph, neo4j.predicates)

        if not paths:
            return None

        document = yaml_structured_document(paths)

        return postprocess(document, is_query)


def yaml_structured_document(paths):
    marker = '<files>'
    document = {marker: []}

    for path in paths:
        attach_path_to_document(path, document, marker)

    return yaml.dump(document)


def attach_path_to_document(branch, trunk, marker):
    """
    Insert a branch of directories on its trunk.
    """
    parts = branch.split('/', 1)
    if len(parts) == 1:  # branch is a file
        trunk[marker].append(parts[0])
    else:
        node, others = parts
        if node not in trunk:
            trunk[node] = {marker: []}
        attach_path_to_document(others, trunk[node], marker)


def build_paths(contribution_subgraph, neo4j_predicates):
    """
    returns a list of paths representing the contribution_subgraph.
    All paths are starting with the contribution label and recursively expanding to the deepest label
    """
    paths = []

    # raw creation
    for part in contribution_subgraph:

        # if contribution label equals a statement's object then avoid cyclic resources;
        if contribution_subgraph[0]['subject'] == part['object']:
            continue

        try:
            path = '/{}/{}/{}'.format(preprocess(part['subject']), preprocess(neo4j_predicates[part['predicate']]),
                                      preprocess(part['object']))
        except KeyError:
            # This problem occurs when the predicates are not cleanly stored in the neo4j data. This issue must be solved from the backend system.
            path = '/{}/{}/{}'.format(preprocess(part['subject']), 'none', preprocess(part['object']))

        paths.append(path)

    i = 0
    while paths_are_not_structured(paths) and i < ITERATING_THRESHOLD:

        for path in paths:
            paths_for_object = get_paths_for_object(paths, os.path.basename(path))

            # replacing the object by the found paths
            if paths_for_object:
                index = paths.index(path)
                paths[index: index + 1] = [path[: path.rfind('/')] + '/' + x for x in paths_for_object]
                break

        # removing the found paths
        for path_for_object in paths_for_object:
            paths.remove(path_for_object)

        i += 1

    if i == ITERATING_THRESHOLD:
        return None

    return paths


def get_paths_for_object(paths, object):
    """
    returns a list of paths starting with the given object
    """
    paths_for_object = []

    for path in paths:
        if path.startswith('/' + object + '/'):
            paths_for_object.append(path)

    return paths_for_object


def paths_are_not_structured(paths):
    """
    returns true if the list of paths are not yet file system structured.
    i.e. if not all paths start with the root path (contribution label)
    """
    if not paths:
        return False

    root = paths[0][: paths[0].find('/', 1)]

    for path in reversed(paths):
        if not path.startswith(root):
            return True

    return False


def preprocess(string):
    if not string:
        return string

    string = string.replace('/', ' ')

    return string


def postprocess(string, is_query=False):
    if not string:
        return string

    # replace each occurrence of one of the following characters with ''
    characters = ['<files>', '\[]', '\[', '\]', ':', '\?', '\'']
    regex = '|'.join(characters)
    string = re.sub(regex, '', string)

    # replace each occurrence of one of the following characters with ' '
    characters = ['\s+-\s+']
    regex = '|'.join(characters)
    string = re.sub(regex, ' ', string)

    # apply escaping for ES reserved characters 
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#_reserved_characters
    if is_query:
        string = escape_es_query(string)

    # terms are lower-cased and only seperated by a space character
    return ' '.join(string.split()).lower()


escape_rules = {
    '+': r'\\+',
    '-': r'\\-',
    '&': r'\\&',
    '|': r'\\|',
    '!': r'\\!',
    '(': r'\\(',
    ')': r'\\)',
    '{': r'\\{',
    '}': r'\\}',
    '^': r'\\^',
    '~': r'\\~',
    '*': r'\\*',
    '"': r'\"',
    '/': r'\\/',
    '>': r' ',
    '<': r' '}


def escaped_seq(term):
    """ Yield the next string based on the
        next character (either this char
        or escaped version """
    for char in term:
        if char in escape_rules.keys():
            yield escape_rules[char]
        else:
            yield char


def escape_es_query(query):
    """ Apply escaping to the passed in query terms
        escaping special characters like : , etc"""
    term = query.replace('\\', r'\\')  # escape \ first
    return "".join([nextStr for nextStr in escaped_seq(term)])
