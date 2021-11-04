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
from itertools import product

import pm4py
from pm4py.algo.discovery.inductive.variants.im_clean import utils as im_utils
from pm4py.objects.log.obj import EventLog


def detect(dfg, alphabet, start_activities, end_activities, msd=None):
    groups = [{a} for a in alphabet]
    if len(groups) == 0:
        return None
    for a, b in product(alphabet, alphabet):
        if (a, b) not in dfg or (b, a) not in dfg:
            groups = im_utils.__merge_groups_for_acts(a, b, groups)
        elif msd is not None:
            if (a in msd and b in msd[a]) or (b in msd and a in msd[b]):
                groups = im_utils.__merge_groups_for_acts(a, b, groups)

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
