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
from pm4py.algo.discovery.inductive.variants.im_clean import utils as imut


def detect(log: EventLog, alphabet: Dict[str, int], use_msd: bool) -> Optional[str]:
    candidates = alphabet
    for t in log:
        candidates = candidates.intersection(set(map(lambda e: e, t)))
        if len(candidates) == 0:
            return None
    for a in candidates:
        proj = [list(filter(lambda e: e != a, t)) for t in log]
        if len(list(filter(lambda t: len(t) == 0, proj))) == 0:
            dfg_proj = imut.discover_dfg(proj)
            alphabet_proj = imut.get_alphabet(proj)
            start_act_proj = imut.get_start_activities(proj)
            end_act_proj = imut.get_end_activities(proj)
            pre_proj, post_proj = dfg_utils.get_transitive_relations(
                dfg_proj, alphabet_proj)
            cut = sequence_cut.detect(alphabet_proj, pre_proj, post_proj)
            if cut is not None:
                return a
            cut = xor_cut.detect(dfg_proj, alphabet_proj)
            if cut is not None:
                return a
            cut = concurrent_cut.detect(dfg_proj, alphabet_proj, start_act_proj, end_act_proj,
                                        msd=imut.msdw(log, imut.msd(log)) if use_msd else None)
            if cut is not None:
                return a
            cut = loop_cut.detect(dfg_proj, alphabet_proj,
                                  start_act_proj, end_act_proj)
            if cut is not None:
                return a
    return None


def project(log: EventLog, activity: str) -> List[List]:
    return [[list(filter(lambda e: e == activity, t)) for t in log], [list(filter(lambda e: e != activity, t)) for t in log]]
