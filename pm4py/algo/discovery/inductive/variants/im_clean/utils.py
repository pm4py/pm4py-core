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
import networkx as nx


def transform_dfg_to_directed_nx_graph(dfg, alphabet):
    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from(alphabet)
    for a, b in dfg:
        nx_graph.add_edge(a, b)
    return nx_graph


def __merge_groups_for_acts(a, b, groups):
    group_a = None
    group_b = None
    for group in groups:
        if a in group:
            group_a = group
        if b in group:
            group_b = group
    groups = [group for group in groups if group != group_a and group != group_b]
    groups.append(group_a.union(group_b))
    return groups
