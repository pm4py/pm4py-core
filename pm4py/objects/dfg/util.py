from collections import Counter
from typing import Dict, Collection, Any

from pm4py.objects.dfg.obj import DFG


def get_vertices(dfg: DFG) -> Collection[Any]:
    """
    Returns the vertices of the dfg

    :param dfg: input directly follows graph

    :rtype: ``Collection[Any]``
    """
    alphabet = set()
    [alphabet.update({a, b}) for (a, b, f) in dfg.graph]
    return alphabet


def get_outgoing_arcs(dfg: DFG) -> Dict[Any, Counter[Any]]:
    """
    Returns the outgoing arcs of the provided DFG graph.
    Returns a dictionary mapping each 'source' node onto its set of 'target' nodes and associated frequency.

    :param dfg: ``DFG`` object

    :rtype: ``Dict[str, Counter[str]]``

    """
    outgoing = {a: Counter() for a in get_vertices(dfg)}
    for (a, b, f) in dfg.graph:
        outgoing[a][b] = f if b not in outgoing[a] else outgoing[a][b] + f
    return outgoing


def get_incoming_arcs(dfg: DFG) -> Dict[Any, Counter[Any]]:
    """
    Returns the incoming arcs of the provided DFG graph.
    Returns a dictionary mapping each 'target' node onto its set of 'source' nodes and associated frequency.

    :param dfg: ``DFG`` object

    :rtype: ``Dict[str, Counter[str]]``

    """
    incoming = {a: Counter() for a in get_vertices(dfg)}
    for (a, b, f) in dfg.graph:
        incoming[b][a] = f if a not in incoming[b] else incoming[b][a] + f
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
