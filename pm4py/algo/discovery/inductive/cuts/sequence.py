from collections import Counter
from itertools import product
import sys
from pm4py.algo.discovery.inductive.variants.im_clean import utils as im_utils
from pm4py.objects.log.obj import EventLog, Trace

def detect(alphabet, trp, trs):
    '''
    This method finds a sequence cut in the dfg.
    Implementation follows function sequence on page 188 of
    "Robust Process Mining with Guarantees" by Sander J.J. Leemans (ISBN: 978-90-386-4257-4)

    Basic Steps:
    1. create a group per activity
    2. merge pairwise reachable nodes (based on transitive relations)
    3. merge pairwise unreachable nodes (based on transitive relations)
    4. sort the groups based on their reachability

    Parameters
    ----------
    alphabet
        characters occurring in the dfg
    trp
        dictionary mapping activities to their (transitive) predecessors, according to the DFG
    transitive_successors
        dictionary mapping activities to their (transitive) successors, according to the DFG

    Returns
    -------
        A list of sets of activities, i.e., forming a maximal sequence cut
        None if no cut is found.

    '''
    groups = [{a} for a in alphabet]
    if len(groups) == 0:
        return None
    for a, b in product(alphabet, alphabet):
        if (b in trs[a] and a in trs[b]) or (
                b not in trs[a] and a not in trs[b]):
            groups = im_utils.__merge_groups_for_acts(a, b, groups)

    groups = list(sorted(groups, key=lambda g: len(
        trp[next(iter(g))]) + (len(alphabet) - len(trs[next(iter(g))]))))
    return groups if len(groups) > 1 else None


def project(log, groups):
    '''
    This method projects the log based on a presumed sequence cut and a list of activity groups
    Parameters
    ----------
    log
        original log
    groups
        list of activity sets to be used in projection (activities can only appear in one group)

    Returns
    -------
        list of corresponding logs according to the sequence cut.
    '''
    logs = [[] for g in groups]
    for t in log:
        i = 0
        split_point = 0
        act_union = set()
        while i < len(groups):
            new_split_point = find_split_point(
                t, groups[i], split_point, act_union)
            trace_i = []
            j = split_point
            while j < new_split_point:
                if t[j] in groups[i]:
                    trace_i.append(t[j])
                j = j + 1
            logs[i].append(trace_i)
            split_point = new_split_point
            act_union = act_union.union(set(groups[i]))
            i = i + 1
    return logs


def find_split_point(t, group, start, ignore):
    least_cost = 0
    position_with_least_cost = start
    cost = 0
    i = start
    while i < len(t):
        if t[i] in group:
            cost = cost - 1
        elif t[i] not in ignore:
            cost = cost + 1

        if cost < least_cost:
            least_cost = cost
            position_with_least_cost = i + 1

        i = i + 1

    return position_with_least_cost


def _is_strict_subset(A, B):
    return A != B and A.issubset(B)


def _is_strict_superset(A, B):
    return A != B and A.issuperset(B)


def project_dfg(dfg_sa_ea_actcount, groups):
    start_activities = []
    end_activities = []
    activities = []
    dfgs = []
    skippable = []
    for g in groups:
        skippable.append(False)
    activities_idx = {}
    for gind, g in enumerate(groups):
        for act in g:
            activities_idx[act] = int(gind)
    i = 0
    while i < len(groups):
        to_succ_arcs = Counter()
        from_prev_arcs = Counter()
        if i < len(groups) - 1:
            for arc in dfg_sa_ea_actcount.dfg:
                if arc[0] in groups[i] and arc[1] in groups[i + 1]:
                    to_succ_arcs[arc[0]] += dfg_sa_ea_actcount.dfg[arc]

        if i > 0:
            for arc in dfg_sa_ea_actcount.dfg:
                if arc[0] in groups[i - 1] and arc[1] in groups[i]:
                    from_prev_arcs[arc[1]] += dfg_sa_ea_actcount.dfg[arc]

        if i == 0:
            start_activities.append({})
            for act in dfg_sa_ea_actcount.start_activities:
                if act in groups[i]:
                    start_activities[i][act] = dfg_sa_ea_actcount.start_activities[act]
                else:
                    j = i
                    while j < activities_idx[act]:
                        skippable[j] = True
                        j = j + 1
        else:
            start_activities.append(from_prev_arcs)

        if i == len(groups) - 1:
            end_activities.append({})
            for act in dfg_sa_ea_actcount.end_activities:
                if act in groups[i]:
                    end_activities[i][act] = dfg_sa_ea_actcount.end_activities[act]
                else:
                    j = activities_idx[act] + 1
                    while j <= i:
                        skippable[j] = True
                        j = j + 1
        else:
            end_activities.append(to_succ_arcs)

        activities.append({})
        for act in groups[i]:
            activities[i][act] = dfg_sa_ea_actcount.act_count[act]
        dfgs.append({})
        for arc in dfg_sa_ea_actcount.dfg:
            if arc[0] in groups[i] and arc[1] in groups[i]:
                dfgs[i][arc] = dfg_sa_ea_actcount.dfg[arc]

        i = i + 1

    i = 0
    while i < len(dfgs):
        dfgs[i] = im_utils.DfgSaEaActCount(
            dfgs[i], start_activities[i], end_activities[i], activities[i])
        i = i + 1
    for arc in dfg_sa_ea_actcount.dfg:
        z = activities_idx[arc[1]]
        j = activities_idx[arc[0]] + 1
        while j < z:
            skippable[j] = False
            j = j + 1
    return [dfgs, skippable]

