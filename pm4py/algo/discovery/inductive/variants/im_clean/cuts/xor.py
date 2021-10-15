from typing import Optional, Dict

from pm4py.algo.discovery.inductive.variants.im_clean import utils as im_utils
from pm4py.algo.discovery.inductive.variants.im_clean.d_types import DFG, Cut
from pm4py.objects.log.obj import EventLog, Trace


def detect(dfg: DFG, alphabet: Dict[str, int]) -> Optional[Cut]:
    '''
    This method finds a xor cut in the dfg.
    Implementation follows function XorCut on page 188 of
    "Robust Process Mining with Guarantees" by Sander J.J. Leemans (ISBN: 978-90-386-4257-4)

    Basic Steps:
    1.) the dfg is transformed to its undirected equivalent.
    2.) we detect the connected components in the graph.
    3.) if there are more than one connected components, the cut exists and is non-minimal.

    Parameters
    ----------
    dfg
        input directly follows graph
    alphabet
        alphabet of the dfg

    Returns
    -------
        A list of sets of activities, i.e., forming a maximal xor cut
        None if no cut is found.

    '''
    import networkx as nx

    nx_dfg = im_utils.transform_dfg_to_directed_nx_graph(dfg, alphabet)
    nx_und = nx_dfg.to_undirected()
    conn_comps = [nx_und.subgraph(c).copy() for c in nx.connected_components(nx_und)]
    if len(conn_comps) > 1:
        cuts = list()
        for comp in conn_comps:
            cuts.append(set(comp.nodes))
        return cuts
    else:
        return None


def project(log, groups, activity_key):
    # refactored to support both IM and IMf
    logs = list()
    for group in groups:
        logs.append(EventLog())
    for t in log:
        count = {i: 0 for i in range(len(groups))}
        for index, group in enumerate(groups):
            for e in t:
                if e[activity_key] in group:
                    count[index] += 1
        count = sorted(list((x, y) for x, y in count.items()), key=lambda x: (x[1], x[0]), reverse=True)
        new_trace = Trace()
        for e in t:
            if e[activity_key] in groups[count[0][0]]:
                new_trace.append(e)
        logs[count[0][0]].append(new_trace)
    return logs


def project_dfg(dfg_sa_ea_actcount, groups):
    dfgs = []
    skippable = []
    for gind, g in enumerate(groups):
        start_activities = {}
        end_activities = {}
        activities = {}
        paths_frequency = {}
        for act in dfg_sa_ea_actcount.start_activities:
            if act in g:
                start_activities[act] = dfg_sa_ea_actcount.start_activities[act]
        for act in dfg_sa_ea_actcount.end_activities:
            if act in g:
                end_activities[act] = dfg_sa_ea_actcount.end_activities[act]
        for act in dfg_sa_ea_actcount.act_count:
            if act in g:
                activities[act] = dfg_sa_ea_actcount.act_count[act]
        for arc in dfg_sa_ea_actcount.dfg:
            if arc[0] in g and arc[1] in g:
                paths_frequency[arc] = dfg_sa_ea_actcount.dfg[arc]
        dfgs.append(im_utils.DfgSaEaActCount(paths_frequency, start_activities, end_activities, activities))
        skippable.append(False)
    return [dfgs, skippable]
