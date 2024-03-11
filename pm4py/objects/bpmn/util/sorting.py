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
from typing import Iterable, List, Tuple
from pm4py.objects.bpmn.obj import BPMN

def bfs_bpmn(nodes: Iterable[BPMN.Event], edges: Iterable[Tuple[BPMN.Event, BPMN.Event]]):
    start_nodes: List[BPMN.Event] = [n for n in nodes if isinstance(n, BPMN.StartEvent)]
    level = 0
    bfs = {n: level for n in start_nodes}
    while True:
        level += 1
        to_visit = list(e[1] for e in edges if e[0] in bfs and e[1] not in bfs and not isinstance(e[1], BPMN.EndEvent))
        if not to_visit:
            break
        for n in to_visit:
            bfs[n] = level
    other_nodes = [n for n in nodes if n not in bfs]
    level += 1
    for n in other_nodes:
        bfs[n] = level
    return bfs


def get_sorted_nodes_edges(bpmn_graph: BPMN) -> Tuple[List[BPMN.Event], List[Tuple[BPMN.Event, BPMN.Event]]]:
    """
    Assure an ordering as-constant-as-possible

    Parameters
    --------------
    bpmn_graph
        BPMN graph

    Returns
    --------------
    nodes
        List of nodes of the BPMN graph
    edges
        List of edges of the BPMN graph
    """
    graph = bpmn_graph.get_graph()
    graph_nodes: List[BPMN.Event] = list(graph.nodes(data=False))
    graph_edges: List[Tuple[BPMN.Event, BPMN.Event]] = list(graph.edges(data=False))
    bfs = bfs_bpmn(graph_nodes, graph_edges)
    graph_nodes = sorted(graph_nodes, key=lambda x: bfs[x])
    graph_edges = sorted(graph_edges, key=lambda x: (bfs[x[0]], bfs[x[1]]))
    return graph_nodes, graph_edges
