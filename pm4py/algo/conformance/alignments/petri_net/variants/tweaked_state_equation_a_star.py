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
import heapq
import sys
import time
from copy import copy
from enum import Enum

from pm4py import util as pm4pyutil
from pm4py.algo.analysis.marking_equation.variants import classic as marking_equation
from pm4py.objects.log import obj as log_implementation
from pm4py.objects.petri_net.utils import align_utils as utils
from pm4py.objects.petri_net.utils.incidence_matrix import construct as inc_mat_construct
from pm4py.objects.petri_net.utils.synchronous_product import construct_cost_aware, construct
from pm4py.objects.petri_net import semantics
from pm4py.objects.petri_net.utils.petri_utils import construct_trace_net_cost_aware, decorate_places_preset_trans, \
    decorate_transitions_prepostset
from pm4py.util import exec_utils
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.objects.petri_net import properties

from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import Trace
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.util import typing


class Parameters(Enum):
    PARAM_TRACE_COST_FUNCTION = 'trace_cost_function'
    PARAM_MODEL_COST_FUNCTION = 'model_cost_function'
    PARAM_SYNC_COST_FUNCTION = 'sync_cost_function'
    PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE = 'ret_tuple_as_trans_desc'
    PARAM_TRACE_NET_COSTS = "trace_net_costs"
    TRACE_NET_CONSTR_FUNCTION = "trace_net_constr_function"
    TRACE_NET_COST_AWARE_CONSTR_FUNCTION = "trace_net_cost_aware_constr_function"
    PARAM_MAX_ALIGN_TIME_TRACE = "max_align_time_trace"
    PARAM_MAX_ALIGN_TIME = "max_align_time"
    PARAMETER_VARIANT_DELIMITER = "variant_delimiter"
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    VARIANTS_IDX = "variants_idx"


PARAM_TRACE_COST_FUNCTION = Parameters.PARAM_TRACE_COST_FUNCTION.value
PARAM_MODEL_COST_FUNCTION = Parameters.PARAM_MODEL_COST_FUNCTION.value
PARAM_SYNC_COST_FUNCTION = Parameters.PARAM_SYNC_COST_FUNCTION.value


def get_best_worst_cost(petri_net, initial_marking, final_marking, parameters=None):
    """
    Gets the best worst cost of an alignment

    Parameters
    -----------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    -----------
    best_worst_cost
        Best worst cost of alignment
    """
    if parameters is None:
        parameters = {}
    trace = log_implementation.Trace()

    best_worst = apply(trace, petri_net, initial_marking, final_marking, parameters=parameters)

    if best_worst is not None:
        return best_worst['cost']

    return None


def apply(trace: Trace, petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> typing.AlignmentResult:
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
        Parameters.PARAM_SYNC_COST_FUNCTION: :class:`dict` (parameter) mapping of each transition in the model to corresponding
        synchronous costs
        Parameters.ACTIVITY_KEY: :class:`str` (parameter) key to use to identify the activity described by the events

    Returns
    -------
    dictionary: `dict` with keys **alignment**, **cost**, **visited_states**, **queued_states** and **traversed_arcs**
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)
    trace_cost_function = exec_utils.get_param_value(Parameters.PARAM_TRACE_COST_FUNCTION, parameters, None)
    model_cost_function = exec_utils.get_param_value(Parameters.PARAM_MODEL_COST_FUNCTION, parameters, None)
    trace_net_constr_function = exec_utils.get_param_value(Parameters.TRACE_NET_CONSTR_FUNCTION, parameters,
                                                           None)
    trace_net_cost_aware_constr_function = exec_utils.get_param_value(Parameters.TRACE_NET_COST_AWARE_CONSTR_FUNCTION,
                                                                      parameters, construct_trace_net_cost_aware)

    if trace_cost_function is None:
        trace_cost_function = list(
            map(lambda e: utils.STD_MODEL_LOG_MOVE_COST, trace))
        parameters[Parameters.PARAM_TRACE_COST_FUNCTION] = trace_cost_function

    if model_cost_function is None:
        # reset variables value
        model_cost_function = dict()
        sync_cost_function = dict()
        for t in petri_net.transitions:
            if t.label is not None:
                model_cost_function[t] = utils.STD_MODEL_LOG_MOVE_COST
                sync_cost_function[t] = utils.STD_SYNC_COST
            else:
                model_cost_function[t] = utils.STD_TAU_COST
        parameters[Parameters.PARAM_MODEL_COST_FUNCTION] = model_cost_function
        parameters[Parameters.PARAM_SYNC_COST_FUNCTION] = sync_cost_function

    if trace_net_constr_function is not None:
        # keep the possibility to pass TRACE_NET_CONSTR_FUNCTION in this old version
        trace_net, trace_im, trace_fm = trace_net_constr_function(trace, activity_key=activity_key)
    else:
        trace_net, trace_im, trace_fm, parameters[
            Parameters.PARAM_TRACE_NET_COSTS] = trace_net_cost_aware_constr_function(trace,
                                                                                     trace_cost_function,
                                                                                     activity_key=activity_key)

    alignment = apply_trace_net(petri_net, initial_marking, final_marking, trace_net, trace_im, trace_fm, parameters)
    return alignment


def apply_from_variant(variant, petri_net, initial_marking, final_marking, parameters=None):
    """
    Apply the alignments from the specification of a single variant

    Parameters
    -------------
    variant
        Variant (as string delimited by the "variant_delimiter" parameter)
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm (same as 'apply' method, plus 'variant_delimiter' that is , by default)

    Returns
    ------------
    dictionary: `dict` with keys **alignment**, **cost**, **visited_states**, **queued_states** and **traversed_arcs**
    """
    if parameters is None:
        parameters = {}
    activity_key = DEFAULT_NAME_KEY if parameters is None or PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters else \
        parameters[
            pm4pyutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    trace = log_implementation.Trace()
    variant_delimiter = exec_utils.get_param_value(Parameters.PARAMETER_VARIANT_DELIMITER, parameters,
                                                   pm4pyutil.constants.DEFAULT_VARIANT_SEP)
    variant_split = variant.split(variant_delimiter) if type(variant) is str else variant
    for i in range(len(variant_split)):
        trace.append(log_implementation.Event({activity_key: variant_split[i]}))
    return apply(trace, petri_net, initial_marking, final_marking, parameters=parameters)


def apply_from_variants_dictionary(var_dictio, petri_net, initial_marking, final_marking, parameters=None):
    """
    Apply the alignments from the specification of a variants dictionary

    Parameters
    -------------
    var_dictio
        Dictionary of variants (along possibly with their count, or the list of indexes, or the list of involved cases)
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm (same as 'apply' method, plus 'variant_delimiter' that is , by default)

    Returns
    --------------
    dictio_alignments
        Dictionary that assigns to each variant its alignment
    """
    if parameters is None:
        parameters = {}
    dictio_alignments = {}
    for variant in var_dictio:
        dictio_alignments[variant] = apply_from_variant(variant, petri_net, initial_marking, final_marking,
                                                        parameters=parameters)
    return dictio_alignments


def apply_from_variants_list(var_list, petri_net, initial_marking, final_marking, parameters=None):
    """
    Apply the alignments from the specification of a list of variants in the log

    Parameters
    -------------
    var_list
        List of variants (for each item, the first entry is the variant itself, the second entry may be the number of cases)
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm (same as 'apply' method, plus 'variant_delimiter' that is , by default)

    Returns
    --------------
    dictio_alignments
        Dictionary that assigns to each variant its alignment
    """
    if parameters is None:
        parameters = {}
    start_time = time.time()
    max_align_time = exec_utils.get_param_value(Parameters.PARAM_MAX_ALIGN_TIME, parameters,
                                                sys.maxsize)
    max_align_time_trace = exec_utils.get_param_value(Parameters.PARAM_MAX_ALIGN_TIME_TRACE, parameters,
                                                      sys.maxsize)
    dictio_alignments = {}
    for varitem in var_list:
        this_max_align_time = min(max_align_time_trace, (max_align_time - (time.time() - start_time)) * 0.5)
        variant = varitem[0]
        parameters[Parameters.PARAM_MAX_ALIGN_TIME_TRACE] = this_max_align_time
        dictio_alignments[variant] = apply_from_variant(variant, petri_net, initial_marking, final_marking,
                                                        parameters=parameters)
    return dictio_alignments


def apply_from_variants_list_petri_string(var_list, petri_net_string, parameters=None):
    """
    Apply the alignments from the specification of a list of variants in the log

    Parameters
    -------------
    var_list
        List of variants (for each item, the first entry is the variant itself, the second entry may be the number of cases)
    petri_net_string
        String representing the accepting Petri net

    Returns
    --------------
    dictio_alignments
        Dictionary that assigns to each variant its alignment
    """
    if parameters is None:
        parameters = {}

    from pm4py.objects.petri_net.importer.variants import pnml as petri_importer

    petri_net, initial_marking, final_marking = petri_importer.import_petri_from_string(petri_net_string)

    res = apply_from_variants_list(var_list, petri_net, initial_marking, final_marking, parameters=parameters)
    return res


def apply_from_variants_list_petri_string_mprocessing(mp_output, var_list, petri_net_string, parameters=None):
    """
    Apply the alignments from the specification of a list of variants in the log

    Parameters
    -------------
    mp_output
        Multiprocessing output
    var_list
        List of variants (for each item, the first entry is the variant itself, the second entry may be the number of cases)
    petri_net_string
        String representing the accepting Petri net

    Returns
    --------------
    dictio_alignments
        Dictionary that assigns to each variant its alignment
    """
    if parameters is None:
        parameters = {}

    res = apply_from_variants_list_petri_string(var_list, petri_net_string, parameters=parameters)
    mp_output.put(res)


def apply_trace_net(petri_net, initial_marking, final_marking, trace_net, trace_im, trace_fm, parameters=None):
    """
        Performs the basic alignment search, given a trace net and a net.

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
            Parameters.PARAM_SYNC_COST_FUNCTION: :class:`dict` (parameter) mapping of each transition in the model to corresponding
            synchronous costs
            Parameters.ACTIVITY_KEY: :class:`str` (parameter) key to use to identify the activity described by the events
            Parameters.PARAM_TRACE_NET_COSTS: :class:`dict` (parameter) mapping between transitions and costs

        Returns
        -------
        dictionary: `dict` with keys **alignment**, **cost**, **visited_states**, **queued_states** and **traversed_arcs**
        """
    if parameters is None:
        parameters = {}

    ret_tuple_as_trans_desc = exec_utils.get_param_value(Parameters.PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE,
                                                         parameters, False)

    trace_cost_function = exec_utils.get_param_value(Parameters.PARAM_TRACE_COST_FUNCTION, parameters, None)
    model_cost_function = exec_utils.get_param_value(Parameters.PARAM_MODEL_COST_FUNCTION, parameters, None)
    sync_cost_function = exec_utils.get_param_value(Parameters.PARAM_SYNC_COST_FUNCTION, parameters, None)
    trace_net_costs = exec_utils.get_param_value(Parameters.PARAM_TRACE_NET_COSTS, parameters, None)

    if trace_cost_function is None or model_cost_function is None or sync_cost_function is None:
        sync_prod, sync_initial_marking, sync_final_marking = construct(trace_net, trace_im,
                                                                        trace_fm, petri_net,
                                                                        initial_marking,
                                                                        final_marking,
                                                                        utils.SKIP)
        cost_function = utils.construct_standard_cost_function(sync_prod, utils.SKIP)
    else:
        revised_sync = dict()
        for t_trace in trace_net.transitions:
            for t_model in petri_net.transitions:
                if t_trace.label == t_model.label:
                    revised_sync[(t_trace, t_model)] = sync_cost_function[t_model]

        sync_prod, sync_initial_marking, sync_final_marking, cost_function = construct_cost_aware(
            trace_net, trace_im, trace_fm, petri_net, initial_marking, final_marking, utils.SKIP,
            trace_net_costs, model_cost_function, revised_sync)

    max_align_time_trace = exec_utils.get_param_value(Parameters.PARAM_MAX_ALIGN_TIME_TRACE, parameters,
                                                      sys.maxsize)

    return apply_sync_prod(sync_prod, sync_initial_marking, sync_final_marking, cost_function,
                           utils.SKIP, ret_tuple_as_trans_desc=ret_tuple_as_trans_desc,
                           max_align_time_trace=max_align_time_trace)


def apply_sync_prod(sync_prod, initial_marking, final_marking, cost_function, skip, ret_tuple_as_trans_desc=False,
                    max_align_time_trace=sys.maxsize):
    return __search(sync_prod, initial_marking, final_marking, cost_function, skip,
                    ret_tuple_as_trans_desc=ret_tuple_as_trans_desc, max_align_time_trace=max_align_time_trace)


def __search(sync_net, ini, fin, cost_function, skip, ret_tuple_as_trans_desc=False,
             max_align_time_trace=sys.maxsize):
    start_time = time.time()

    decorate_transitions_prepostset(sync_net)
    decorate_places_preset_trans(sync_net)

    incidence_matrix = inc_mat_construct(sync_net)
    ini_vec, fin_vec, cost_vec = utils.__vectorize_initial_final_cost(incidence_matrix, ini, fin, cost_function)

    closed = set()
    heu_dict = {}
    heu_max_ind_dict = {}
    mtcgt_dict = {}

    parameters = {}
    parameters[marking_equation.Parameters.FULL_BOOTSTRAP_REQUIRED] = False
    parameters[marking_equation.Parameters.INCIDENCE_MATRIX] = incidence_matrix
    parameters[marking_equation.Parameters.COSTS] = cost_function

    visited = 0
    queued = 0
    traversed = 0
    me = marking_equation.build(sync_net, ini, fin, parameters=parameters)
    h, x = me.solve()
    lp_solved = 1

    # try to see if the firing sequence is already fine
    firing_sequence, reach_fm, explained_events = me.get_firing_sequence(x)
    if reach_fm:
        return __reconstruct_alignment(firing_sequence, h, visited, queued, traversed,
                                       ret_tuple_as_trans_desc=ret_tuple_as_trans_desc, lp_solved=lp_solved)
    mm, index = __get_model_marking_and_index(ini)
    __update_heu_dict(heu_dict, heu_max_ind_dict, mm, index, h, x, firing_sequence, incidence_matrix, cost_vec)

    ini_state = utils.TweakedSearchTuple(0 + h, 0, h, ini, None, None, x, True, False)
    open_set = [ini_state]
    heapq.heapify(open_set)

    trans_empty_preset = set(t for t in sync_net.transitions if len(t.in_arcs) == 0)

    while not len(open_set) == 0:
        if (time.time() - start_time) > max_align_time_trace:
            return None

        curr = heapq.heappop(open_set)

        current_marking = curr.m

        while not curr.trust:
            if (time.time() - start_time) > max_align_time_trace:
                return None

            already_closed = current_marking in closed
            if already_closed:
                curr = heapq.heappop(open_set)
                current_marking = curr.m
                continue

            if curr.t not in mtcgt_dict:
                lp_solved += 1
                mtcgt = __min_total_cost_given_trans(me, ini, incidence_matrix, curr.t)
                mtcgt_dict[curr.t] = mtcgt
            else:
                mtcgt = mtcgt_dict[curr.t]

            h1 = max(mtcgt - curr.g, 0)
            if h1 > curr.h:
                tp = utils.TweakedSearchTuple(curr.g + h1, curr.g, h1, curr.m, curr.p, curr.t, curr.x, False, False)
                curr = heapq.heappushpop(open_set, tp)
                current_marking = curr.m
                continue

            mm, index = __get_model_marking_and_index(curr.m)
            h2, x2, trust2 = __get_heu_from_dict(heu_dict, heu_max_ind_dict, mm, index)
            if h2 is not None and h2 > curr.h:
                tp = utils.TweakedSearchTuple(curr.g + h2, curr.g, h2, curr.m, curr.p, curr.t, x2, trust2, False)
                curr = heapq.heappushpop(open_set, tp)
                current_marking = curr.m
                continue

            me.change_ini_vec(curr.m)
            h, x = me.solve()

            __update_heu_dict_specific_point(heu_dict, heu_max_ind_dict, mm, index, h, x)

            lp_solved += 1
            tp = utils.TweakedSearchTuple(curr.g + h, curr.g, h, curr.m, curr.p, curr.t, x, True, True)
            curr = heapq.heappushpop(open_set, tp)
            current_marking = curr.m

        already_closed = current_marking in closed
        if already_closed:
            continue
        if curr.h < 0.01:
            if current_marking == fin:
                trans_list = __transitions_list_from_state(curr)
                return __reconstruct_alignment(trans_list, curr.f, visited, queued, traversed,
                                               ret_tuple_as_trans_desc=ret_tuple_as_trans_desc, lp_solved=lp_solved)

        if curr.virgin:
            # try to see if the firing sequence is already fine
            firing_sequence, reach_fm, explained_events = me.get_firing_sequence(curr.x)
            if reach_fm:
                trans_list = __transitions_list_from_state(curr) + list(firing_sequence)
                return __reconstruct_alignment(trans_list, curr.f, visited, queued, traversed,
                                               ret_tuple_as_trans_desc=ret_tuple_as_trans_desc, lp_solved=lp_solved)
            mm, index = __get_model_marking_and_index(curr.m)
            __update_heu_dict(heu_dict, heu_max_ind_dict, mm, index, h, x, firing_sequence, incidence_matrix, cost_vec)

        closed.add(current_marking)
        visited += 1

        enabled_trans = copy(trans_empty_preset)
        for p in current_marking:
            for t in p.ass_trans:
                if t.sub_marking <= current_marking:
                    enabled_trans.add(t)

        trans_to_visit_with_cost = [(t, cost_function[t]) for t in enabled_trans if not (
                t is not None and utils.__is_log_move(t, skip) and utils.__is_model_move(t, skip))]

        for t, cost in trans_to_visit_with_cost:
            traversed += 1
            new_marking = utils.add_markings(current_marking, t.add_marking)

            if new_marking in closed:
                continue
            g = curr.g + cost

            queued += 1
            h, x = utils.__derive_heuristic(incidence_matrix, cost_vec, curr.x, t, curr.h)
            trust = utils.__trust_solution(x)
            mm, index = __get_model_marking_and_index(new_marking)

            if not trust:
                h2, x2, trust2 = __get_heu_from_dict(heu_dict, heu_max_ind_dict, mm, index)
                if h2 is not None and (h2 > h or trust2):
                    h = h2
                    x = x2
                    trust = trust2
            else:
                __update_heu_dict_specific_point(heu_dict, heu_max_ind_dict, mm, index, h, x)

            new_f = g + h
            tp = utils.TweakedSearchTuple(new_f, g, h, new_marking, curr, t, x, trust, False)
            heapq.heappush(open_set, tp)


def __min_total_cost_given_trans(mark_eq, ini, incidence_matrix, t):
    """
    Searches the minimum total cost assumed by the marking equation
    starting from the initial marking and passing through the transition "t"

    Parameters
    --------------
    mark_eq
        Marking equation
    ini
        Initial marking
    incidence_matrix
        Incidence matrix
    t
        Transition

    Returns
    ----------------
    h
        Heuristics from the initial marking passing through t
    """
    mark_eq.change_ini_vec(ini)
    import numpy as np
    tind = incidence_matrix.transitions[t]
    c, Aub, bub, Aeq, beq = mark_eq.c, mark_eq.Aub, mark_eq.bub, mark_eq.Aeq, mark_eq.beq
    Aub_appendix = np.zeros((1, Aub.shape[1]))
    bub_appendix = -np.eye(1)
    Aub_appendix[0, tind] = -1
    Aub = np.vstack([Aub, Aub_appendix])
    bub = np.vstack([bub, bub_appendix])
    h, x = mark_eq.solve_given_components(c, Aub, bub, Aeq, beq)
    return h


def __update_heu_dict(heu_dict, heu_max_ind_dict, mm, index, h, x, firing_sequence, incidence_matrix, cost_vec):
    """
    Updates the heuristics dictionary on the new marking, storing the information about the heuristics
    and the vector
    """
    x = copy(x)
    __update_heu_dict_specific_point(heu_dict, heu_max_ind_dict, mm, index, h, x)
    firing_sequence = list(firing_sequence)
    while firing_sequence:
        t = firing_sequence.pop(0)
        h, x = utils.__derive_heuristic(incidence_matrix, cost_vec, x, t, h)
        mm = semantics.weak_execute(t, mm)
        __update_heu_dict_specific_point(heu_dict, heu_max_ind_dict, mm, index, h, x)


def __update_heu_dict_specific_point(heu_dict, heu_max_ind_dict, mm, index, h, x):
    """
    Updates the heuristics dictionary on the new marking, storing the information about the heuristics
    and the vector (point-specific method)
    """
    if mm not in heu_dict:
        heu_dict[mm] = {}
        heu_max_ind_dict[mm] = -1
    hdm = heu_dict[mm]
    if index not in hdm:
        hdm[index] = (-1, None)
    if h > hdm[index][0]:
        hdm[index] = (h, tuple(x))
    heu_max_ind_dict[mm] = max(heu_max_ind_dict[mm], index)


def __get_heu_from_dict(heu_dict, heu_max_ind_dict, mm, index):
    """
    Retrieves a value for an heuristics that has already been calculated,
    given the marking
    """
    if mm in heu_dict and heu_max_ind_dict[mm] >= index:
        hdm = heu_dict[mm]
        if index in hdm:
            ret = hdm[index]
            return ret[0], list(ret[1]), True

    return None, None, None


def __get_model_marking_and_index(marking):
    """
    Transforms a marking on the synchronous product net
    to a marking in the model and an index in the trace
    """
    mm = Marking()
    index = -1
    for p in marking:
        if properties.TRACE_NET_PLACE_INDEX in p.properties:
            index = p.properties[properties.TRACE_NET_PLACE_INDEX]
        else:
            mm[p] = marking[p]
    return mm, index


def __transitions_list_from_state(curr):
    """
    Gets the list of transitions visited throughout the
    current state
    """
    ret = []
    while curr.p is not None:
        ret.append(curr.t)
        curr = curr.p
    ret.reverse()
    return ret


def __reconstruct_alignment(trans_list, cost, visited, queued, traversed, ret_tuple_as_trans_desc=False, lp_solved=0):
    """
    Variant-specific reconstruct alignment method
    """
    alignment = []
    if ret_tuple_as_trans_desc:
        for t in trans_list:
            alignment.append((t.name, t.label))
    else:
        for t in trans_list:
            alignment.append(t.label)

    return {"alignment": alignment, "cost": cost, "visited_states": visited, "queued_states": queued,
            "traversed_states": traversed, "lp_solved": lp_solved}
