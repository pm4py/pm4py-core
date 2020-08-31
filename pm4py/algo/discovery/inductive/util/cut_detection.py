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
            comps = [detection_utils.perform_list_union(list(set(strongly_connected_components[i]) for i in comp)) for comp in
                     comps]
            return [True, comps]
    return [False, [], []]
