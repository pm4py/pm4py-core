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

import time
import sys
from pm4py.objects.petri_net.utils import align_utils
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util import exec_utils
from pm4py.objects.petri_net.semantics import enabled_transitions
from enum import Enum
from copy import copy
import heapq
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import Trace
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.util import typing


class Parameters(Enum):
    PARAM_TRACE_COST_FUNCTION = 'trace_cost_function'
    PARAM_MODEL_COST_FUNCTION = 'model_cost_function'
    PARAM_STD_SYNC_COST = 'std_sync_cost'
    PARAM_MAX_ALIGN_TIME_TRACE = "max_align_time_trace"
    PARAM_MAX_ALIGN_TIME = "max_align_time"
    PARAMETER_VARIANT_DELIMITER = "variant_delimiter"
    PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE = 'ret_tuple_as_trans_desc'
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY


PLACES_DICT = "places_dict"
INV_TRANS_DICT = "inv_trans_dict"
LABELS_DICT = "labels_dict"
TRANS_LABELS_DICT = "trans_labels_dict"
TRANS_PRE_DICT = "trans_pre_dict"
TRANS_POST_DICT = "trans_post_dict"
TRANSF_IM = "transf_im"
TRANSF_FM = "transf_fm"
TRANSF_MODEL_COST_FUNCTION = "transf_model_cost_function"
TRANSF_TRACE = "transf_trace"
TRACE_COST_FUNCTION = "trace_cost_function"
INV_TRACE_LABELS_DICT = "inv_trace_labels_dict"

IS_SYNC_MOVE = 0
IS_LOG_MOVE = 1
IS_MODEL_MOVE = 2

POSITION_TOTAL_COST = 0
POSITION_INDEX = 1
POSITION_TYPE_MOVE = 2
POSITION_ALIGN_LENGTH = 3
POSITION_STATES_COUNT = 4
POSITION_PARENT_STATE = 5
POSITION_MARKING = 6
POSITION_EN_T = 7


def __transform_model_to_mem_efficient_structure(net, im, fm, trace, parameters=None):
    """
    Transform the Petri net model to a memory efficient structure

    Parameters
    --------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    trace
        Trace
    parameters
        Parameters

    Returns
    --------------
    model_struct
        Model data structure, including:
            PLACES_DICT: associates each place to a number
            INV_TRANS_DICT: associates a number to each transition
            LABELS_DICT: labels dictionary (a label to a number)
            TRANS_LABELS_DICT: associates each transition to the number corresponding to its label
            TRANS_PRE_DICT: preset of a transition, expressed as in this data structure
            TRANS_POST_DICT: postset of a transition, expressed as in this data structure
            TRANSF_IM: transformed initial marking
            TRANSF_FM: transformed final marking
            TRANSF_MODEL_COST_FUNCTION: transformed model cost function
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)
    labels = sorted(list(set(x[activity_key] for x in trace)))

    model_cost_function = exec_utils.get_param_value(Parameters.PARAM_MODEL_COST_FUNCTION, parameters, None)

    if model_cost_function is None:
        model_cost_function = {}
        for t in net.transitions:
            if t.label is not None:
                model_cost_function[t] = align_utils.STD_MODEL_LOG_MOVE_COST
            else:
                preset_t = Marking()
                for a in t.in_arcs:
                    preset_t[a.source] = a.weight
                en_t = enabled_transitions(net, preset_t)
                vis_t_trace = [t for t in en_t if t.label in labels]
                if len(vis_t_trace) == 0:
                    model_cost_function[t] = align_utils.STD_TAU_COST
                else:
                    model_cost_function[t] = align_utils.STD_TAU_COST

    places_dict = {place: index for index, place in enumerate(net.places)}
    trans_dict = {trans: index for index, trans in enumerate(net.transitions)}

    labels = sorted(list(set(t.label for t in net.transitions if t.label is not None)))
    labels_dict = {labels[i]: i for i in range(len(labels))}

    trans_labels_dict = {}
    for t in net.transitions:
        trans_labels_dict[trans_dict[t]] = labels_dict[t.label] if t.label is not None else None

    trans_pre_dict = {trans_dict[t]: {places_dict[x.source]: x.weight for x in t.in_arcs} for t in
                      net.transitions}
    trans_post_dict = {trans_dict[t]: {places_dict[x.target]: x.weight for x in t.out_arcs} for t in
                       net.transitions}

    transf_im = {places_dict[p]: im[p] for p in im}
    transf_fm = {places_dict[p]: fm[p] for p in fm}

    transf_model_cost_function = {trans_dict[t]: model_cost_function[t] for t in net.transitions}

    inv_trans_dict = {y: x for x, y in trans_dict.items()}

    return {PLACES_DICT: places_dict, INV_TRANS_DICT: inv_trans_dict, LABELS_DICT: labels_dict,
            TRANS_LABELS_DICT: trans_labels_dict, TRANS_PRE_DICT: trans_pre_dict,
            TRANS_POST_DICT: trans_post_dict,
            TRANSF_IM: transf_im, TRANSF_FM: transf_fm, TRANSF_MODEL_COST_FUNCTION: transf_model_cost_function}


def __transform_trace_to_mem_efficient_structure(trace, model_struct, parameters=None):
    """
    Transforms a trace to a memory efficient structure

    Parameters
    ---------------
    trace
        Trace
    model_struct
        Efficient data structure for the model (calculated above)
    parameters
        Parameters

    Returns
    ---------------
    trace_struct
        An efficient structure describing the trace, including:
            TRANSF_TRACE: the transformed trace
            TRACE_COST_FUNCTION: the cost function associated to the trace
            INV_TRACE_LABELS_DICT: dictionary that associates a number to an activity
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)

    trace_cost_function = exec_utils.get_param_value(Parameters.PARAM_TRACE_COST_FUNCTION, parameters, None)
    if trace_cost_function is None:
        trace_cost_function = {i: align_utils.STD_MODEL_LOG_MOVE_COST for i in range(len(trace))}

    labels = sorted(list(set(x[activity_key] for x in trace)))
    labels_dict = copy(model_struct[LABELS_DICT])

    for l in labels:
        if l not in labels_dict:
            labels_dict[l] = len(labels_dict)

    transf_trace = [labels_dict[x[activity_key]] for x in trace]

    inv_trace_labels_dict = {y: x for x, y in labels_dict.items()}
    return {TRANSF_TRACE: transf_trace, TRACE_COST_FUNCTION: trace_cost_function,
            INV_TRACE_LABELS_DICT: inv_trace_labels_dict}


def apply(trace: Trace, net: PetriNet, im: Marking, fm: Marking, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> typing.AlignmentResult:
    """
    Performs the basic alignment search, given a trace and a net.

    Parameters
    ----------
    trace: :class:`list` input trace, assumed to be a list of events (i.e. the code will use the activity key
    to get the attributes)
    petri_net: :class:`pm4py.objects.petri.net.PetriNet` the Petri net to use in the alignment
    initial_marking: :class:`pm4py.objects.petri.net.Marking` initial marking in the Petri net
    final_marking: :class:`pm4py.objects.petri.net.Marking` final marking in the Petri net
    parameters: :class:`dict` (optional) dictionary containing one of the following:
        Parameters.PARAM_TRACE_COST_FUNCTION: :class:`list` (parameter) mapping of each index of the trace to a positive cost value
        Parameters.PARAM_MODEL_COST_FUNCTION: :class:`dict` (parameter) mapping of each transition in the model to corresponding
        model cost
        Parameters.ACTIVITY_KEY: :class:`str` (parameter) key to use to identify the activity described by the events

    Returns
    -------
    dictionary: `dict` with keys **alignment**, **cost**, **visited_states**, **queued_states** and **traversed_arcs**
    """
    if parameters is None:
        parameters = {}

    model_struct = __transform_model_to_mem_efficient_structure(net, im, fm, trace, parameters=parameters)
    trace_struct = __transform_trace_to_mem_efficient_structure(trace, model_struct, parameters=parameters)

    sync_cost = exec_utils.get_param_value(Parameters.PARAM_STD_SYNC_COST, parameters, align_utils.STD_SYNC_COST)
    max_align_time_trace = exec_utils.get_param_value(Parameters.PARAM_MAX_ALIGN_TIME_TRACE, parameters,
                                                      sys.maxsize)
    ret_tuple_as_trans_desc = exec_utils.get_param_value(Parameters.PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE,
                                                         parameters, False)

    return __dijkstra(model_struct, trace_struct, sync_cost=sync_cost, max_align_time_trace=max_align_time_trace,
                      ret_tuple_as_trans_desc=ret_tuple_as_trans_desc)


def __dict_leq(d1, d2):
    """
    Checks if the first dictionary is <= the second

    Parameters
    --------------
    d1
        First dictionary
    d2
        Second dictionary

    Returns
    --------------
    boolean
        Boolean
    """
    for k in d1:
        if k not in d2:
            return False
        if d1[k] > d2[k]:
            return False
    return True


def __fire_trans(m, preset, postset):
    """
    Fires a transition and returns a new marking

    Parameters
    ---------------
    m
        Marking
    preset
        Preset
    postset
        Postset

    Returns
    ---------------
    new_m
        New marking
    """
    ret = {}
    for k in m:
        if k in preset:
            diff = m[k] - preset[k]
            if diff > 0:
                ret[k] = diff
        else:
            ret[k] = m[k]
    for k in postset:
        if k not in ret:
            ret[k] = postset[k]
        else:
            ret[k] = ret[k] + postset[k]
    return ret


def __encode_marking(marking_dict, m_d):
    """
    Encode a marking using the dictionary

    Parameters
    --------------
    marking_dict
        Marking dictionary
    m_d
        Current marking (dict)

    Returns
    --------------
    m_t
        Marking in tuple
    """
    keys = sorted(list(m_d.keys()))
    m_t = []
    for el in keys:
        for i in range(m_d[el]):
            m_t.append(el)
    m_t = tuple(m_t)
    if m_t not in marking_dict:
        marking_dict[m_t] = m_t
    return marking_dict[m_t]


def __decode_marking(m_t):
    """
    Decode a marking using a dictionary

    Parameters
    ---------------
    m_t
        Marking as tuple

    Returns
    ---------------
    m_d
        Marking as dictionary
    """
    m_d = {}
    for el in m_t:
        if el not in m_d:
            m_d[el] = 1
        else:
            m_d[el] = m_d[el] + 1

    return m_d


def __check_closed(closed, ns):
    """
    Checks if the state is closed

    Parameters
    -------------
    closed
        Closed set
    ns
        New state (marking, index)

    Returns
    -------------
    bool
        Boolean (true if the state is closed)
    """
    if ns[0] in closed:
        if closed[ns[0]] < ns[1]:
            return True
        elif closed[ns[0]] == ns[1]:
            return False
    return False


def __add_closed(closed, ns):
    """
    Adds a closed state

    Parameters
    --------------
    closed
        Closed set
    ns
        New state (marking, index)
    """
    closed[ns[0]] = ns[1]


def __add_to_open_set(open_set, ns):
    """
    Adds a new state to the open set whether necessary

    Parameters
    ----------------
    open_set
        Open set
    ns
        New state
    """
    """
    shall_add = True
    shall_heapify = False
    i = 0
    while i < len(open_set):
        if open_set[i][POSITION_MARKING] == ns[POSITION_MARKING]:
            if open_set[i][POSITION_INDEX] <= ns[POSITION_INDEX] and open_set[i][POSITION_TOTAL_COST] <= ns[
                POSITION_TOTAL_COST]:
                # do not add anything
                shall_add = False
                break
            if open_set[i][POSITION_INDEX] >= ns[POSITION_INDEX] and open_set[i][POSITION_TOTAL_COST] > ns[
                POSITION_TOTAL_COST]:
                del open_set[i]
                shall_heapify = True
                continue
        i = i + 1
    if shall_add:
        heapq.heappush(open_set, ns)
    if shall_heapify:
        heapq.heapify(open_set)
    """
    # the previous code minimizes memory occupation on microcontrollers, but maybe is not worthy
    # the performance price on larger memory computers
    heapq.heappush(open_set, ns)
    return open_set


def __dijkstra(model_struct, trace_struct, sync_cost=align_utils.STD_SYNC_COST, max_align_time_trace=sys.maxsize,
               ret_tuple_as_trans_desc=False):
    """
    Alignments using Dijkstra

    Parameters
    ---------------
    model_struct
        Efficient model structure
    trace_struct
        Efficient trace structure
    sync_cost
        Cost of a sync move (limitation: all sync moves shall have the same cost in this setting)
    max_align_time_trace
        Maximum alignment time for a trace (in seconds)
    ret_tuple_as_trans_desc
        Says if the alignments shall be constructed including also
        the name of the transition, or only the label (default=False includes only the label)

    Returns
    --------------
    alignment
        Alignment of the trace, including:
            alignment: the sequence of moves
            queued: the number of states that have been queued
            visited: the number of states that have been visited
            cost: the cost of the alignment
    """
    start_time = time.time()

    trans_pre_dict = model_struct[TRANS_PRE_DICT]
    trans_post_dict = model_struct[TRANS_POST_DICT]
    trans_labels_dict = model_struct[TRANS_LABELS_DICT]
    transf_model_cost_function = model_struct[TRANSF_MODEL_COST_FUNCTION]

    transf_trace = trace_struct[TRANSF_TRACE]
    trace_cost_function = trace_struct[TRACE_COST_FUNCTION]

    marking_dict = {}
    im = __encode_marking(marking_dict, model_struct[TRANSF_IM])
    fm = __encode_marking(marking_dict, model_struct[TRANSF_FM])

    # each state is characterized by:
    # position 0 (POSITION_TOTAL_COST): total cost of the state
    # position 1 (POSITION_INDEX): the opposite of the position of the trace (the higher is, the lower should
    # be the state in the queue
    # position 2 (POSITION_TYPE_MOVE): the type of the move:
    # ----------- 0 (IS_SYNC_MOVE): sync moves
    # ----------- 1 (IS_LOG_MOVE): log moves
    # ----------- 2 (IS_MODEL_MOVE): model moves
    # position 3 (POSITION_ALIGN_LENGTH): the length of the alignment
    # position 4 (POSITION_STATES_COUNT): the count of states visited
    # position 5 (POSITION_PARENT_STATE): if valued, the parent state of the current state
    # position 6 (POSITION_MARKING): the marking associated to the state
    # position 7 (POSITION_EN_T): if valued, the transition that was enabled to reach the state
    initial_state = (0, 0, 0, 0, 0, None, im, None)
    open_set = [initial_state]
    heapq.heapify(open_set)

    closed = {}
    dummy_count = 0
    visited = 0

    opt_cost = sys.maxsize
    visited_sequences = set()

    while not len(open_set) == 0:
        if (time.time() - start_time) > max_align_time_trace:
            return None
        curr = heapq.heappop(open_set)
        curr_m0 = curr[POSITION_MARKING]
        curr_m = __decode_marking(curr_m0)
        # if a situation equivalent to the one of the current state has been
        # visited previously, then discard this
        if __check_closed(closed, (curr_m0, curr[POSITION_INDEX])):
            continue
        visited = visited + 1

        curr_cost = curr[POSITION_TOTAL_COST]
        if curr_cost > opt_cost:
            break

        if curr_m0 == fm:
            if -curr[POSITION_INDEX] == len(transf_trace):
                opt_cost = curr_cost
                ali = __reconstruct_alignment(curr, model_struct, trace_struct, visited, len(open_set), len(closed),
                                               len(marking_dict),
                                               ret_tuple_as_trans_desc=ret_tuple_as_trans_desc)
                ali_sequence = tuple(ali["alignment"])
                if ali_sequence not in visited_sequences:
                    visited_sequences.add(ali_sequence)
                    yield ali
                continue
        __add_closed(closed, (curr_m0, curr[POSITION_INDEX]))

        # retrieves the transitions that are enabled in the current marking
        en_t = [t for t in trans_pre_dict if __dict_leq(trans_pre_dict[t], curr_m)]
        j = 0
        while j < len(en_t):
            t = en_t[j]
            # checks if a given transition can be executed in sync with the trace
            is_sync = trans_labels_dict[t] == transf_trace[-curr[POSITION_INDEX]] if -curr[POSITION_INDEX] < len(
                transf_trace) else False
            if is_sync:
                dummy_count = dummy_count + 1
                # virtually fires the transition to get a new marking
                new_m = __encode_marking(marking_dict,
                                         __fire_trans(curr_m, trans_pre_dict[t], trans_post_dict[t]))
                new_state = (
                    curr[POSITION_TOTAL_COST] + sync_cost, curr[POSITION_INDEX] - 1, IS_SYNC_MOVE,
                    curr[POSITION_ALIGN_LENGTH] + 1, dummy_count,
                    curr,
                    new_m, t)
                if not __check_closed(closed, (new_state[POSITION_MARKING], new_state[POSITION_INDEX])):
                    # if it can be executed in a sync way, add a new state corresponding
                    # to the sync execution only if it has not already been closed
                    open_set = __add_to_open_set(open_set, new_state)
                del en_t[j]
                continue
            j = j + 1
        en_t.sort(key=lambda t: transf_model_cost_function[t])
        j = 0
        while j < len(en_t):
            t = en_t[j]
            dummy_count = dummy_count + 1
            # virtually fires the transition to get a new marking
            new_m = __encode_marking(marking_dict,
                                     __fire_trans(curr_m, trans_pre_dict[t], trans_post_dict[t]))
            new_state = (
                curr[POSITION_TOTAL_COST] + transf_model_cost_function[t], curr[POSITION_INDEX], IS_MODEL_MOVE,
                curr[POSITION_ALIGN_LENGTH] + 1, dummy_count, curr, new_m, t)
            if not curr_m0 == new_m:
                if not __check_closed(closed, (new_state[POSITION_MARKING], new_state[POSITION_INDEX])):
                    open_set = __add_to_open_set(open_set, new_state)
            j = j + 1

        # IMPORTANT: to reduce the complexity, assume that you can schedule a log move
        # only if the previous move has not been a move-on-model.
        # since this setting is equivalent to scheduling all the log moves before and then
        # the model moves
        if -curr[POSITION_INDEX] < len(transf_trace) and curr[POSITION_TYPE_MOVE] != IS_MODEL_MOVE:
            dummy_count = dummy_count + 1
            new_state = (
                curr[POSITION_TOTAL_COST] + trace_cost_function[-curr[POSITION_INDEX]], curr[POSITION_INDEX] - 1,
                IS_LOG_MOVE, curr[POSITION_ALIGN_LENGTH] + 1, dummy_count, curr, curr_m0, None)
            if not __check_closed(closed, (new_state[POSITION_MARKING], new_state[POSITION_INDEX])):
                # adds the log move only if it has not been already closed before
                open_set = __add_to_open_set(open_set, new_state)


def __reconstruct_alignment(curr, model_struct, trace_struct, visited, open_set_length, closed_set_length,
                            num_visited_markings, ret_tuple_as_trans_desc=False):
    """
    Reconstruct the alignment from the final state (that reached the final marking)

    Parameters
    ----------------
    curr
        Current state (final state)
    model_struct
        Efficient data structure for the model
    trace_struct
        Efficient data structure for the trace
    visited
        Number of visited states
    open_set_length
        Length of the open set
    closed_set_length
        Length of the closed set
    num_visited_markings
        Number of visited markings
    ret_tuple_as_trans_desc
        Says if the alignments shall be constructed including also
        the name of the transition, or only the label (default=False includes only the label)

    Returns
    --------------
    alignment
        Alignment of the trace, including:
            alignment: the sequence of moves
            queued: the number of states that have been queued
            visited: the number of states that have been visited
            cost: the cost of the alignment
    """
    transf_trace = trace_struct[TRANSF_TRACE]
    inv_labels_dict = trace_struct[INV_TRACE_LABELS_DICT]
    inv_trans_dict = model_struct[INV_TRANS_DICT]

    alignment = []
    cost = curr[POSITION_TOTAL_COST]
    queued = open_set_length + visited

    while curr[POSITION_PARENT_STATE] is not None:
        m_name, m_label, t_name, t_label = ">>", ">>", ">>", ">>"
        if curr[POSITION_TYPE_MOVE] == IS_SYNC_MOVE or curr[POSITION_TYPE_MOVE] == IS_LOG_MOVE:
            name = inv_labels_dict[transf_trace[-curr[POSITION_INDEX] - 1]]
            t_name, t_label = name, name
        if curr[POSITION_TYPE_MOVE] == IS_SYNC_MOVE or curr[POSITION_TYPE_MOVE] == IS_MODEL_MOVE:
            t = inv_trans_dict[curr[POSITION_EN_T]]
            m_name, m_label = t.name, t.label

        if ret_tuple_as_trans_desc:
            alignment = [((t_name, m_name), (t_label, m_label))] + alignment
        else:
            alignment = [(t_label, m_label)] + alignment
        curr = curr[POSITION_PARENT_STATE]

    return {"alignment": alignment, "cost": cost, "queued_states": queued, "visited_states": visited,
            "closed_set_length": closed_set_length, "num_visited_markings": num_visited_markings}
