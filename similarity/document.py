import os
import networkx as nx

import orkg
import re

from orkg import ORKG


class DocumentCreator:

    @staticmethod
    def create(contribution_id, is_query=False):
        """
        creates a document for a contribution_id
        """
        # TODO: move the connection creation to a proper place
        client = ORKG(host=os.getenv('ORKG_API_HOST', 'localhost'))

        try:
            graph = orkg.subgraph(client=client, thing_id=contribution_id, blacklist='ResearchField')
        except ValueError:
            # TODO: add logging here
            return None

        document = []
        node_to_nodes = {}
        for u, v in nx.bfs_edges(graph, source=contribution_id):
            node_to_nodes.setdefault(u, []).append(v)

        for u, V in node_to_nodes.items():
            document.append(graph.nodes[u]['label'])

            visited_edges = []
            for v in V:

                edge = graph.edges[(u, v)]['label']
                if edge not in visited_edges:
                    document.append(edge)
                    visited_edges.append(edge)

                document.append(graph.nodes[v]['label'])

        document = ' '.join(document)
        return postprocess(document, is_query)


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
