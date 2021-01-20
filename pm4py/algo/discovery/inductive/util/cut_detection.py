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
from pm4py.algo.discovery.inductive.util import detection_utils


def detect_sequential_cut(subtree, dfg, strongly_connected_components):
    """
    Detect sequential cut in DFG graph

    Parameters
    --------------
    dfg
        DFG
    strongly_connected_components
        Strongly connected components
    """
    if subtree.contains_empty_trace():
        return [False, [], []]
    if len(strongly_connected_components) > 1:
        conn_matrix = detection_utils.get_connection_matrix(strongly_connected_components, dfg)
        comps = []
        closed = set()
        for i in range(conn_matrix.shape[0]):
            if max(conn_matrix[i, :]) == 0:
                if len(comps) == 0:
                    comps.append([])
                comps[-1].append(i)
                closed.add(i)
        cyc_continue = len(comps) >= 1
        while cyc_continue:
            cyc_continue = False
            curr_comp = []
            for i in range(conn_matrix.shape[0]):
                if i not in closed:
                    i_j = set()
                    for j in range(conn_matrix.shape[1]):
                        if conn_matrix[i][j] == 1.0:
                            i_j.add(j)
                    i_j_minus = i_j.difference(closed)
                    if len(i_j_minus) == 0:
                        curr_comp.append(i)
                        closed.add(i)
            if curr_comp:
                cyc_continue = True
                comps.append(curr_comp)
        last_cond = False
        for i in range(conn_matrix.shape[0]):
            if i not in closed:
                if not last_cond:
                    last_cond = True
                    comps.append([])
                comps[-1].append(i)
        if len(comps) > 1:
            comps = [detection_utils.perform_list_union(list(set(strongly_connected_components[i]) for i in comp)) for
                     comp in
                     comps]

            # this part assures that the sequential cut follows completely the definition, i.e. there are no
            # subsequent components with no edges between them (except when the detected cut is binary).
            #
            # Remind: the tree returned by IM is folded at the end, this ensures that the cut is still maximal
            dfg = [x[0] for x in dfg]
            i = 0
            while i < len(comps) - 1:
                outer_edges = [d for d in dfg if d[0] in comps[i] and d[1] not in comps[i] and d[1] not in comps[i + 1]]
                # a situation that is not managed by considering only the outer edges is the one
                # that sees a chain of invisibles at the end. In this case, it can be detected that the end activity
                # has no edge toward any of the following components.
                end_activities_wo_exedge = set(
                    a for a in subtree.end_activities if a in comps[i] and a not in [x[0] for x in dfg])
                # before merging the connected components, make sure that at the end there are two (or more)
                # connected components
                if (outer_edges or end_activities_wo_exedge) and len(comps) > 2:
                    comps[i] = comps[i].union(comps[i + 1])
                    del comps[i + 1]
                    continue
                i = i + 1
            return [True, comps]
    return [False, [], []]
