from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.petri.semantics import is_enabled, weak_execute
from copy import copy
from pm4py.objects.petri.petrinet import Marking


def get_bmap(net, m, bmap):
    """
    Updates the B-map with the invisibles enabling marking m

    Parameters
    --------------
    net
        Petri net
    m
        Marking
    bmap
        B-map

    Returns
    --------------
    trans_list
        List of invisibles that enable m
    """
    if m not in bmap:
        bmap[m] = []
        for t in net.transitions:
            if t.label is None:
                if m <= t.out_marking:
                    bmap[m].append(t)
    return bmap[m]


def diff_mark(m, t):
    """
    Subtract from a marking the postset of t and adds the preset

    Parameters
    ------------
    m
        Marking
    t
        Transition

    Returns
    ------------
    diff_mark
        Difference marking
    """
    for a in t.out_arcs:
        p = a.target
        w = a.weight
        if p in m and w <= m[p]:
            m[p] = m[p] - w
            if m[p] == 0:
                del m[p]
    for a in t.in_arcs:
        p = a.source
        w = a.weight
        if not p in m:
            m[p] = 0
        m[p] = m[p] + w
    return m


def explore_backwards(re_list, all_vis, net, m, bmap):
    """
    Do the backwards state space exploration

    Parameters
    --------------
    re_list
        List of remaining markings to visit using the backwards approach
    all_vis
        Set of visited transitions
    net
        Petri net
    m
        Marking
    bmap
        B-map of the net

    Returns
    ------------
    list_tr
        List of transitions to enable in order to enable a marking (otherwise None)
    """
    i = 0
    while i < len(re_list):
        curr = re_list[i]
        if curr[1] <= m:
            curr[2].reverse()
            return curr[2]
        j = 0
        while j < len(curr[0]):
            if not curr[0][j] in all_vis:
                new_m = diff_mark(copy(curr[1]), curr[0][j])
                re_list.append((get_bmap(net, new_m, bmap), new_m, curr[2] + [curr[0][j]]))
                all_vis.add(curr[0][j])
            j = j + 1
        #print(i, len(re_list), re_list)
        i = i + 1
    return None


def tr_vlist(vlist, net, im, tmap, bmap, parameters=None):
    """
    Visit a variant using the backwards token basedr eplay

    Parameters
    ------------
    vlist
        Variants list
    net
        Petri net
    im
        Initial marking
    tmap
        Transition map (labels to list of transitions)
    bmap
        B-map
    parameters
        Possible parameters of the execution

    Returns
    -------------
    visited_transitions
        List of visited transitions during the replay
    is_fit
        Indicates if the replay was successful or not
    """
    if parameters is None:
        parameters = {}

    m = copy(im)

    visited_transitions = []
    is_fit = True

    for act in vlist:
        if act in tmap:
            for t in tmap[act]:
                if is_enabled(t, net, m):
                    visited_transitions.append(t)
                    m = weak_execute(t, m)
                elif len(tmap[act]) == 1:
                    back_res = explore_backwards([(get_bmap(net, t.in_marking, bmap), copy(t.in_marking), list())], set(), net, m, bmap)
                    if back_res is not None:
                        for t2 in back_res:
                            m = weak_execute(t2, m)
                        visited_transitions = visited_transitions + back_res
                        m = weak_execute(t, m)
                        visited_transitions.append(t)
                    else:
                        is_fit = False
                        return {"visited_transitions": visited_transitions, "is_fit": is_fit}
                else:
                    is_fit = False
                    return {"visited_transitions": visited_transitions, "is_fit": is_fit}

    return {"visited_transitions": visited_transitions, "is_fit": is_fit}

def apply(log, net, initial_marking, final_marking, parameters=None):
    """
    Method to apply token-based replay

    Parameters
    -----------
    log
        Log
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    for t in net.transitions:
        ma = Marking()
        for a in t.out_arcs:
            p = a.target
            ma[p] = a.weight
        t.out_marking = ma

    for t in net.transitions:
        ma = Marking()
        for a in t.in_arcs:
            p = a.source
            ma[p] = a.weight
        t.in_marking = ma

    variants_idxs = variants_filter.get_variants_from_log_trace_idx(log, parameters=parameters)
    results = []

    tmap = {}
    bmap = {}
    for t in net.transitions:
        if t.label is not None:
            if t.label not in tmap:
                tmap[t.label] = []
            tmap[t.label].append(t)

    for variant in variants_idxs:
        vlist = variant.split(",")
        result = tr_vlist(vlist, net, initial_marking, tmap, bmap, parameters=parameters)
        results.append(result)

    al_idx = {}
    for index_variant, variant in enumerate(variants_idxs):
        for trace_idx in variants_idxs[variant]:
            al_idx[trace_idx] = results[index_variant]

    ret = []
    for i in range(len(log)):
        ret.append(al_idx[i])

    return ret
