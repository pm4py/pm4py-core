from pm4py.objects.process_tree import obj as pt
from collections import Counter
import itertools


def compress(log, ak):
    actd = dict()
    lt = []
    cl = list()
    for t in log:
        tc = list()
        for e in t:
            a = e[ak]
            if a not in actd:
                actd[a] = len(lt)
                lt.append(a)
            tc.append(actd[a])
        cl.append(tc)
    return lt, cl

def discover_dfg(cl):
    dfg = Counter()
    for t in cl:
        for i in range(0,len(t)-1):
            dfg.update([(t[i],t[i+1])])
    return dfg


def get_start_activities(cl):
    return set(map(lambda t: t[0], filter(lambda t: len(t) > 0, cl)))

def get_end_activities(cl):
    return set(map(lambda t: t[len(t)-1], filter(lambda t : len(t) > 0, cl)))

def get_alphabet(cl):
    return set(itertools.chain(*cl))

def msd(cl):
    msd = dict()
    alphabet = get_alphabet(cl)
    for a in alphabet:
        if len(list(filter(lambda t: len(t) > 1, list(map(lambda t: list(filter(lambda e: e == a, t)), cl))))) > 0:
            activity_indices = list(
                filter(lambda t: len(t) > 1, list(map(lambda t: [i for i, x in enumerate(t) if x == a], cl))))
            msd[a] = min([i for l in list(
                map(lambda t: [t[i] - t[i - 1] - 1 for i, x in enumerate(t) if i > 0], activity_indices)) for i in l])
    return msd

def msdw(cl, msd):
    witnesses = dict()
    alphabet = get_alphabet(cl)
    for a in alphabet:
        if a in msd and msd[a] > 0:
            witnesses[a] = set()
        else:
            continue
        for t in cl:
            if len(list(filter(lambda e: e == a, t))) > 1:
                indices = [i for i, x in enumerate(t) if x == a]
                for i in range(len(indices) - 1):
                    if indices[i + 1] - indices[i] - 1 == msd[a]:
                        for b in t[indices[i] + 1:indices[i + 1]]:
                            witnesses[a].add(b)
    return witnesses



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
