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
from typing import Dict, Optional, List

import pm4py
from pm4py.algo.discovery.dfg import algorithm as discover_dfg
from pm4py.algo.discovery.inductive.variants.im_clean.cuts import sequence as sequence_cut, loop as loop_cut, \
    xor as xor_cut, concurrency as concurrent_cut
from pm4py.objects.dfg.utils import dfg_utils
from pm4py.objects.log.obj import EventLog
from pm4py.util import constants
from pm4py.algo.discovery.minimum_self_distance import algorithm as msd_algo
from pm4py.algo.discovery.minimum_self_distance import utils as msdw_algo
from pm4py.statistics.end_activities.log import get as get_ends
from pm4py.statistics.start_activities.log import get as get_starters


def detect(log: EventLog, alphabet: Dict[str, int], act_key: str, use_msd: bool) -> Optional[str]:
    candidates = set(alphabet.keys())
    for t in log:
        candidates = candidates.intersection(set(map(lambda e: e[act_key], t)))
        if len(candidates) == 0:
            return None
    for a in candidates:
        proj = EventLog()
        for t in log:
            proj.append(pm4py.filter_trace(lambda e: e[act_key] != a, t))
        if len(list(filter(lambda t: len(t) == 0, proj))) == 0:
            dfg_proj = discover_dfg.apply(proj, parameters={
                constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key})
            alphabet_proj = pm4py.get_event_attribute_values(proj, act_key)
            start_act_proj = get_starters.get_start_activities(proj, parameters={
                constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key})
            end_act_proj = get_ends.get_end_activities(log, parameters={
                constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key})
            pre_proj, post_proj = dfg_utils.get_transitive_relations(dfg_proj, alphabet_proj)
            cut = sequence_cut.detect(alphabet_proj, pre_proj, post_proj)
            if cut is not None:
                return a
            cut = xor_cut.detect(dfg_proj, alphabet_proj)
            if cut is not None:
                return a
            cut = concurrent_cut.detect(dfg_proj, alphabet_proj, start_act_proj, end_act_proj,
                                        msd= msdw_algo.derive_msd_witnesses(proj, msd_algo.apply(log, parameters={
                                        constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key}), parameters={
                                        constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key}) if use_msd else None)
            if cut is not None:
                return a
            cut = loop_cut.detect(dfg_proj, alphabet_proj, start_act_proj, end_act_proj)
            if cut is not None:
                return a
    return None


def project(log: EventLog, activity: str, activity_key: str) -> List[EventLog]:
    proj = EventLog()
    proj_act = EventLog()
    for t in log:
        proj.append(pm4py.filter_trace(lambda e: e[activity_key] != activity, t))
        proj_act.append(pm4py.filter_trace(lambda e: e[activity_key] == activity, t))
    return [proj_act, proj]
