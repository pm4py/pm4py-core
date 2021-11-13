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
from pm4py.objects.process_tree import obj as pt


def transform_dfg_to_directed_nx_graph(dfg, alphabet):
    import networkx as nx

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


def __filter_dfg_on_threshold(dfg, end_activities, threshold):
    outgoing_max_occ = {}
    for x, y in dfg.items():
        act = x[0]
        if act not in outgoing_max_occ:
            outgoing_max_occ[act] = y
        else:
            outgoing_max_occ[act] = max(y, outgoing_max_occ[act])
        if act in end_activities:
            outgoing_max_occ[act] = max(outgoing_max_occ[act], end_activities[act])
    dfg_list = sorted([(x, y) for x, y in dfg.items()], key=lambda x: (x[1], x[0]), reverse=True)
    dfg_list = [x for x in dfg_list if x[1] > threshold * outgoing_max_occ[x[0][0]]]
    dfg_list = [x[0] for x in dfg_list]
    # filter the elements in the DFG
    dfg = {x: y for x, y in dfg.items() if x in dfg_list}
    return dfg


def __flower(alphabet, root):
    operator = pt.ProcessTree(operator=pt.Operator.LOOP, parent=root)
    operator.children.append(pt.ProcessTree(parent=operator))
    xor = pt.ProcessTree(operator=pt.Operator.XOR)
    operator.children.append(xor)
    for a in alphabet:
        tree = pt.ProcessTree(label=a, parent=xor)
        xor.children.append(tree)
    return operator


class DfgSaEaActCount(object):
    def __init__(self, dfg, sa, ea, act_count):
        self.dfg = dfg
        self.start_activities = sa
        self.end_activities = ea
        self.act_count = act_count

    def __str__(self):
        return str((self.dfg, self.start_activities, self.end_activities, self.act_count))

    def __repr__(self):
        return str((self.dfg, self.start_activities, self.end_activities, self.act_count))
