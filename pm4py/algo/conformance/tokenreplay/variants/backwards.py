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
from pm4py.statistics.variants.log import get as variants_filter
from pm4py.objects.petri_net.semantics import is_enabled, weak_execute
from pm4py.objects.petri_net.utils.align_utils import get_visible_transitions_eventually_enabled_by_marking
from copy import copy
from collections import Counter
from pm4py.util import exec_utils, constants, xes_constants, pandas_utils
import warnings
from enum import Enum
from pm4py.util import variants_util
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
import pandas as pd
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.util import typing


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    PARAMETER_VARIANT_DELIMITER = "variant_delimiter"
    VARIANTS = "variants"
    PLACES_SHORTEST_PATH_BY_HIDDEN = "places_shortest_path_by_hidden"
    THREAD_MAX_EX_TIME = "thread_maximum_ex_time"
    DISABLE_VARIANTS = "disable_variants"
    CLEANING_TOKEN_FLOOD = "cleaning_token_flood"
    IS_REDUCTION = "is_reduction"
    WALK_THROUGH_HIDDEN_TRANS = "walk_through_hidden_trans"
    RETURN_NAMES = "return_names"
    STOP_IMMEDIATELY_UNFIT = "stop_immediately_unfit"
    TRY_TO_REACH_FINAL_MARKING_THROUGH_HIDDEN = "try_to_reach_final_marking_through_hidden"
    CONSIDER_REMAINING_IN_FITNESS = "consider_remaining_in_fitness"
    ENABLE_PLTR_FITNESS = "enable_pltr_fitness"


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
        i = i + 1
    return None


def execute_tr(m, t, tokens_counter):
    for a in t.in_arcs:
        sp = a.source
        w = a.weight
        if sp not in m:
            tokens_counter["missing"] += w
        elif w > m[sp]:
            tokens_counter["missing"] += w - m[sp]
        tokens_counter["consumed"] += w
    for a in t.out_arcs:
        tokens_counter["produced"] += a.weight
    new_m = weak_execute(t, m)
    m = new_m
    return m, tokens_counter


def tr_vlist(vlist, net, im, fm, tmap, bmap, parameters=None):
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

    stop_immediately_unfit = exec_utils.get_param_value(Parameters.STOP_IMMEDIATELY_UNFIT, parameters, False)

    m = copy(im)
    tokens_counter = Counter()
    tokens_counter["missing"] = 0
    tokens_counter["remaining"] = 0
    tokens_counter["consumed"] = 0
    tokens_counter["produced"] = 0

    for p in m:
        tokens_counter["produced"] += m[p]

    visited_transitions = []
    transitions_with_problems = []

    is_fit = True
    replay_interrupted = False
    for act in vlist:
        if act in tmap:
            rep_ok = False
            for t in tmap[act]:
                if is_enabled(t, net, m):
                    m, tokens_counter = execute_tr(m, t, tokens_counter)
                    visited_transitions.append(t)
                    rep_ok = True
                    continue
                elif len(tmap[act]) == 1:
                    back_res = explore_backwards([(get_bmap(net, t.in_marking, bmap), copy(t.in_marking), list())],
                                                 set(), net, m, bmap)
                    if back_res is not None:
                        rep_ok = True
                        for t2 in back_res:
                            m, tokens_counter = execute_tr(m, t2, tokens_counter)
                        visited_transitions = visited_transitions + back_res
                        m, tokens_counter = execute_tr(m, t, tokens_counter)
                        visited_transitions.append(t)
                    else:
                        is_fit = False
                        transitions_with_problems.append(t)
                        m, tokens_counter = execute_tr(m, t, tokens_counter)
                        visited_transitions.append(t)
                        if stop_immediately_unfit:
                            rep_ok = False
                            break
                        else:
                            rep_ok = True
            if not rep_ok:
                is_fit = False
                replay_interrupted = True
                break

    if not m == fm:
        is_fit = False
        diff1 = m - fm
        diff2 = fm - m
        for p in diff1:
            if diff1[p] > 0:
                tokens_counter["remaining"] += diff1[p]
        for p in diff2:
            if diff2[p] > 0:
                tokens_counter["missing"] += diff2[p]

    for p in fm:
        tokens_counter["consumed"] += m[p]

    trace_fitness = 0.5 * (1.0 - float(tokens_counter["missing"]) / float(tokens_counter["consumed"])) + 0.5 * (
            1.0 - float(tokens_counter["remaining"]) / float(tokens_counter["produced"]))

    enabled_transitions_in_marking = get_visible_transitions_eventually_enabled_by_marking(net, m)

    return {"activated_transitions": visited_transitions, "trace_is_fit": is_fit,
            "replay_interrupted": replay_interrupted, "transitions_with_problems": transitions_with_problems,
            "activated_transitions_labels": [x.label for x in visited_transitions],
            "missing_tokens": tokens_counter["missing"],
            "consumed_tokens": tokens_counter["consumed"],
            "produced_tokens": tokens_counter["produced"],
            "remaining_tokens": tokens_counter["remaining"], "trace_fitness": trace_fitness,
            "enabled_transitions_in_marking": enabled_transitions_in_marking}


def apply(log: EventLog, net: PetriNet, initial_marking: Marking, final_marking: Marking, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> typing.ListAlignments:
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

    if constants.SHOW_INTERNAL_WARNINGS:
        warnings.warn("the backwards variant of TBR will be removed in a future version.")

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
        vlist = variants_util.get_activities_from_variant(variant)
        result = tr_vlist(vlist, net, initial_marking, final_marking, tmap, bmap, parameters=parameters)
        results.append(result)

    al_idx = {}
    for index_variant, variant in enumerate(variants_idxs):
        for trace_idx in variants_idxs[variant]:
            al_idx[trace_idx] = results[index_variant]

    ret = []
    for i in range(len(log)):
        ret.append(al_idx[i])

    return ret


def get_diagnostics_dataframe(log: EventLog, tbr_output: typing.ListAlignments, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> pd.DataFrame:
    """
    Gets the results of token-based replay in a dataframe

    Parameters
    --------------
    log
        Event log
    tbr_output
        Output of the token-based replay technique

    Returns
    --------------
    dataframe
        Diagnostics dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY)

    import pandas as pd

    diagn_stream = []

    for index in range(len(log)):
        case_id = log[index].attributes[case_id_key]
        is_fit = tbr_output[index]["trace_is_fit"]
        trace_fitness = tbr_output[index]["trace_fitness"]
        missing = tbr_output[index]["missing_tokens"]
        remaining = tbr_output[index]["remaining_tokens"]
        produced = tbr_output[index]["produced_tokens"]
        consumed = tbr_output[index]["consumed_tokens"]

        diagn_stream.append({"case_id": case_id, "is_fit": is_fit, "trace_fitness": trace_fitness, "missing": missing, "remaining": remaining, "produced": produced, "consumed": consumed})

    return pandas_utils.instantiate_dataframe(diagn_stream)
