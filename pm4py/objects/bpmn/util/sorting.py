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
def bfs_bpmn(nodes, edges):
    from pm4py.objects.bpmn.obj import BPMN

    start_nodes = [n for n in nodes if isinstance(n, BPMN.StartEvent)]
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


def sort_nodes_given_bfs(nodes, bfs):
    something_changed = True
    while something_changed:
        something_changed = False
        i = 0
        while i < len(nodes):
            name_i = nodes[i].get_name()
            j = i + 1
            while j < len(nodes):
                name_j = nodes[j].get_name()
                should_exchange = False
                if bfs[nodes[i]] > bfs[nodes[j]]:
                    should_exchange = True
                elif bfs[nodes[i]] == bfs[nodes[j]] and name_j and not name_i:
                    should_exchange = True
                elif bfs[nodes[i]] == bfs[nodes[j]] and name_i and name_j and name_i < name_j:
                    should_exchange = True
                if should_exchange:
                    nodes[i], nodes[j] = nodes[j], nodes[i]
                    something_changed = True
                    break
                j = j + 1
            i = i + 1
    return nodes


def sort_edges_given_bfs(edges, bfs):
    something_changed = True
    while something_changed:
        something_changed = False
        i = 0
        while i < len(edges):
            j = i + 1
            while j < len(edges):
                should_exchange = False
                if bfs[edges[i][0]] > bfs[edges[j][0]]:
                    should_exchange = True
                elif bfs[edges[i][0]] == bfs[edges[j][0]] and bfs[edges[i][1]] > bfs[edges[j][1]]:
                    should_exchange = True
                if should_exchange:
                    edges[i], edges[j] = edges[j], edges[i]
                    something_changed = True
                    break
                j = j + 1
            i = i + 1
    return edges


def get_sorted_nodes_edges(bpmn_graph):
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
    graph_nodes = list(graph.nodes(data=False))
    graph_edges = list(graph.edges(data=False))
    bfs = bfs_bpmn(graph_nodes, graph_edges)
    graph_nodes = sort_nodes_given_bfs(graph_nodes, bfs)
    graph_edges = sort_edges_given_bfs(graph_edges, bfs)
    return graph_nodes, graph_edges
