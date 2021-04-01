from itertools import product

import pm4py
from pm4py.algo.discovery.inductive.variants.im_clean import utils
from pm4py.objects.log.obj import EventLog


def detect(dfg, alphabet, start_activities, end_activities, msd=None):
    groups = [{a} for a in alphabet]
    if len(groups) == 0:
        return None
    for a, b in product(alphabet, alphabet):
        if (a, b) not in dfg or (b, a) not in dfg:
            groups = utils.__merge_groups_for_acts(a, b, groups)
        elif msd is not None:
            if (a in msd and b in msd[a]) or (b in msd and a in msd[b]):
                groups = utils.__merge_groups_for_acts(a, b, groups)

    groups = list(sorted(groups, key=lambda g: len(g)))
    i = 0
    while i < len(groups) and len(groups) > 1:
        if len(groups[i].intersection(start_activities)) > 0 and len(groups[i].intersection(end_activities)) > 0:
            i += 1
            continue
        group = groups[i]
        del groups[i]
        if i == 0:
            groups[i].update(group)
        else:
            groups[i - 1].update(group)

    return groups if len(groups) > 1 else None


def project(log, groups, activity_key):
    logs = list()
    for group in groups:
        proj = EventLog()
        for t in log:
            proj.append(pm4py.filter_trace(lambda e: e[activity_key] in group, t))
        logs.append(proj)
    return logs
