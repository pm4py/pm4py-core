'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from collections import Counter
from typing import Dict, Collection, Any, Tuple

from pm4py.util import nx_utils

from pm4py.objects.dfg.obj import DFG


def get_vertices(dfg: DFG) -> Collection[Any]:
    """
    Returns the vertices of the dfg

    :param dfg: input directly follows graph

    :rtype: ``Collection[Any]``
    """
    alphabet = set()
    [alphabet.update({a, b}) for (a, b) in dfg.graph]
    [alphabet.update({a}) for a in dfg.start_activities]
    [alphabet.update({a}) for a in dfg.end_activities]
    return alphabet


def get_outgoing_arcs(dfg: DFG) -> Dict[Any, Dict[Any, int]]:
    """
    Returns the outgoing arcs of the provided DFG graph.
    Returns a dictionary mapping each 'source' node onto its set of 'target' nodes and associated frequency.

    :param dfg: ``DFG`` object

    :rtype: ``Dict[str, Counter[str]]``

    """
    outgoing = {a: Counter() for a in get_vertices(dfg)}
    for (a, b) in dfg.graph:
        outgoing[a][b] = dfg.graph[(a, b)] if b not in outgoing[a] else outgoing[a][b] + dfg.graph[(a, b)]
    return outgoing


def get_incoming_arcs(dfg: DFG) -> Dict[Any, Dict[Any, int]]:
    """
    Returns the incoming arcs of the provided DFG graph.
    Returns a dictionary mapping each 'target' node onto its set of 'source' nodes and associated frequency.

    :param dfg: ``DFG`` object

    :rtype: ``Dict[str, Counter[str]]``

    """
    incoming = {a: Counter() for a in get_vertices(dfg)}
    for (a, b) in dfg.graph:
        incoming[b][a] = dfg.graph[(a, b)] if a not in incoming[b] else incoming[b][a] + dfg.graph[(a, b)]
    return incoming


def get_source_vertices(dfg: DFG) -> Collection[Any]:
    """
    Gets source vertices from a Directly-Follows Graph.
    Vertices are returned that have no incoming arcs

    :param dfg: ``DFG`` object

    :rtype: ``Collection[Any]``
    """
    starters = set()
    incoming = get_incoming_arcs(dfg)
    [starters.add(a) for a in incoming if len(incoming[a]) == 0]
    return starters


def get_sink_vertices(dfg: DFG) -> Collection[Any]:
    """
    Gets sink vertices from a Directly-Follows Graph.
    Vertices are returned that have no outgoing arcs

    :param dfg: ``DFG`` object

    :rtype: ``Collection[Any]``
    """
    ends = set()
    outgoing = get_outgoing_arcs(dfg)
    [ends.add(a) for a in outgoing if len(outgoing[a]) == 0]
    return ends


def get_transitive_relations(dfg: DFG) -> Tuple[Dict[Any, Collection[Any]], Dict[Any, Collection[Any]]]:
    '''
    Computes the full transitive relations in both directions (all activities reachable from a given activity and all
    activities that can reach the activity)

    :param dfg: ``DFG`` object

    :rtype: ``Tuple[Dict[Any, Collection[Any]], Dict[Any, Collection[Any]]] first argument maps an activity on all other
    activities that are able to reach the activity ('transitive pre set')
        second argument maps an activity on all other activities that it can reach (transitively) ('transitive post set')
    '''
    G = nx_utils.DiGraph()
    alph = get_vertices(dfg)

    for act in alph:
        G.add_node(act)

    for edge in dfg.graph:
        G.add_edge(edge[0], edge[1])

    pre = {}
    post = {}

    for a in alph:
        pre[a] = nx_utils.ancestors(G, a)
        post[a] = nx_utils.descendants(G, a)

    return pre, post


def get_vertex_frequencies(dfg: DFG) -> Dict[Any, int]:
    '''
    Computes the number of times a vertex in the dfg is visited.
    The number equals the number of occurrences in the underlying log and is computed by summing up the incoming
    arc frequency and the number of starts in the vertex. The value is equal to the number of outgoing arcs combined
    with the number of endings of the vertex.
    '''
    c = Counter()
    for v in get_vertices(dfg):
        c[v] = 0
    for (a, b) in dfg.graph:
        c[a] += dfg.graph[(a, b)]
    for a in dfg.start_activities:
        c[a] += dfg.start_activities[a]
    return c


def as_nx_graph(dfg: DFG):
    nx_graph = nx_utils.DiGraph()
    nx_graph.add_nodes_from(get_vertices(dfg))
    for a, b in dfg.graph:
        nx_graph.add_edge(a, b)
    return nx_graph


def get_edges(dfg: DFG) -> Collection[Tuple[Any, Any]]:
    return dfg.graph.keys()
