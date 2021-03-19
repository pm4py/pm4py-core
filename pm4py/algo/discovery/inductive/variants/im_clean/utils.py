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
