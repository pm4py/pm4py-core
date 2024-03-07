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
import time
from pm4py import util as pm4pyutil
from pm4py.objects import petri_net
from pm4py.objects.log import obj as log_implementation
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.objects.petri_net.utils.synchronous_product import construct, construct_cost_aware
from pm4py.objects.petri_net.utils.petri_utils import construct_trace_net_cost_aware, decorate_places_preset_trans, \
    decorate_transitions_prepostset
from pm4py.objects.petri_net.utils import align_utils as utils
from pm4py.util import exec_utils
from copy import copy
from enum import Enum
import sys
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY

'''
This version sets a specific heuristic whom paper description is under submission.
It's a transformed verison of the dijkstra_no_heuristic.py file. 
Author: Boltenhagen Mathilde
Date: Nov. 2020
'''


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
    SYNCHRONOUS = "synchronous_dijkstra"
    EXPONENT="exponent"


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

    if best_worst['cost'] > 0:
        return best_worst['cost'] // utils.STD_MODEL_LOG_MOVE_COST
    return 0


def apply(trace, petri_net, initial_marking, final_marking, parameters=None):
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

    parameters = copy(parameters)
    synchro = exec_utils.get_param_value(Parameters.SYNCHRONOUS, parameters, None)
    if  synchro is None or synchro:
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
                    sync_cost_function[t] = 0
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
    else :
        expo = exec_utils.get_param_value(Parameters.EXPONENT, parameters, None)
        if expo is None:
            expo=2
        alignment = __search_without_synchr(petri_net, initial_marking, final_marking,trace, expo=expo)
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
    if parameters is None:
        parameters = {}

    from pm4py.objects.petri_net.importer.variants import pnml as petri_importer

    petri_net, initial_marking, final_marking = petri_importer.import_petri_from_string(petri_net_string)

    res = apply_from_variants_list(var_list, petri_net, initial_marking, final_marking, parameters=parameters)
    return res


def apply_from_variants_list_petri_string_mprocessing(mp_output, var_list, petri_net_string, parameters=None):
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
    expo = exec_utils.get_param_value(Parameters.EXPONENT, parameters, None)
    if expo is None:
        expo=2
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

    return apply_sync_prod(sync_prod, sync_initial_marking, sync_final_marking,
                           utils.SKIP, ret_tuple_as_trans_desc=ret_tuple_as_trans_desc,
                           max_align_time_trace=max_align_time_trace, expo=expo)


def apply_sync_prod(sync_prod, initial_marking, final_marking, skip, ret_tuple_as_trans_desc=False,
                    max_align_time_trace=sys.maxsize, expo=2):
    return __search_with_synchr(sync_prod, initial_marking, final_marking, skip,
                                ret_tuple_as_trans_desc=ret_tuple_as_trans_desc, max_align_time_trace=max_align_time_trace,
                                expo=expo)


def __search_with_synchr(sync_net, ini, fin, skip, ret_tuple_as_trans_desc=False,
                         max_align_time_trace=sys.maxsize, expo=2):
    '''
    In this function that can be called with the following way:
            alignment.algorithm.apply(trace, net, marking, fmarking,variant=ali.VERSION_DIJKSTRA_EXPONENTIAL_HEURISTIC,
                                parameters={ali.Parameters.SYNCHRONOUS:True})
    Cost of transition depends on the run of the synchronous product.
    Other parameters:
    ali.Parameters.EXPONENT:2 (change the base of the log)
    '''
    start_time = time.time()
    decorate_transitions_prepostset(sync_net)
    decorate_places_preset_trans(sync_net)
    closed = {}


    ini_state = utils.DijkstraSearchTuple(0, ini, None, None, 0)
    open_set = [ini_state]
    heapq.heapify(open_set)
    visited = 0
    queued = 0
    traversed = 0

    def cost_function(t,l, expo):
        if t.label is None:
            return expo**(-l)
        if t.label[1]==utils.SKIP or  t.label[0]==utils.SKIP:
            return expo**(-l)
        else :
            return 0

    trans_empty_preset = set(t for t in sync_net.transitions if len(t.in_arcs) == 0)

    while not len(open_set) == 0:
        if (time.time() - start_time) > max_align_time_trace:
            return None

        curr = heapq.heappop(open_set)

        current_marking = curr.m
        already_closed = current_marking in closed.keys()

        if already_closed  :
            continue

        if current_marking == fin:
            return utils.__reconstruct_alignment(curr, visited, queued, traversed,
                                                 ret_tuple_as_trans_desc=ret_tuple_as_trans_desc)

        closed[current_marking]=curr.l
        visited += 1

        possible_enabling_transitions = copy(trans_empty_preset)
        for p in current_marking:
            for t in p.ass_trans:
                possible_enabling_transitions.add(t)

        enabled_trans = [t for t in possible_enabling_transitions if t.sub_marking <= current_marking]
        trans_to_visit_with_cost = [(t, cost_function(t,curr.l,expo)) for t in enabled_trans if  t is not None ]

        for t, cost in trans_to_visit_with_cost:
            traversed += 1
            new_marking = utils.add_markings(current_marking, t.add_marking)

            already_closed = new_marking in closed.keys()
            if already_closed:
                continue

            queued += 1

            tp = utils.DijkstraSearchTuple(curr.g + cost, new_marking, curr, t, curr.l + 1)

            heapq.heappush(open_set, tp)

def __search_without_synchr(net, ini, fin, log_trace, skip= utils.SKIP, ret_tuple_as_trans_desc=True,
                            max_align_time_trace=sys.maxsize,expo=2):
    '''
    In this function that can be called with the following way:
            alignment.algorithm.apply(trace, net, marking, fmarking,variant=ali.VERSION_DIJKSTRA_EXPONENTIAL_HEURISTIC,
                                parameters={ali.Parameters.SYNCHRONOUS:False})
    we compute the distance at each marking. However there is a question:
    Should we keep the entire trace or cut it?
    Notice that the heuristic on marking reachability is ON
    '''
    trace = [log_trace[i]["concept:name"] for i in range(len(log_trace))]
    start_time = time.time()
    decorate_transitions_prepostset(net)
    decorate_places_preset_trans(net)
    closed = {}

    # a node in this version contains the marking state.m[Ø] and the position in the trace state.m[1]
    ini_state = utils.DijkstraSearchTuple(0, (ini,0), None, None, 0)
    open_set = [ini_state]
    heapq.heapify(open_set)
    visited = 0
    queued = 0
    traversed = 0

    def cost_function(t,l, expo):
        if t == utils.SKIP :
            return expo**(-l)
        else :
            return 0

    trans_empty_preset = set(t for t in net.transitions if len(t.in_arcs) == 0)

    while not len(open_set) == 0:

        if (time.time() - start_time) > max_align_time_trace:
            return None

        curr = heapq.heappop(open_set)

        current_marking = curr.m
        already_closed = current_marking in closed.keys()

        if already_closed:
            # if marking has already been visited, we don't visit it again
            # it's a heuristic
            continue

        if current_marking[0] == fin and current_marking[1] == len(trace):
            return utils.__reconstruct_alignment(curr, visited, queued, traversed,
                                                 ret_tuple_as_trans_desc=ret_tuple_as_trans_desc)

        closed[current_marking]=curr.l

        visited += 1

        # ----- either we try to move in model
        possible_enabling_transitions = copy(trans_empty_preset)
        for p in current_marking[0]:
            for t in p.ass_trans:
                possible_enabling_transitions.add(t)

        enabled_trans = [t for t in possible_enabling_transitions if t.sub_marking <= current_marking[0]]

        trans_to_visit_with_cost = [(t, cost_function(utils.SKIP,curr.l,expo)) for t in enabled_trans if t is not None ]
        for t, cost in trans_to_visit_with_cost:
            traversed += 1
            new_marking = (utils.add_markings(current_marking[0], t.add_marking),current_marking[1])

            if new_marking in closed.keys() :
                # if marking has already been visited, we don't visit it again
                # it's a heuristic
                continue

            queued += 1

            tp = utils.DijkstraSearchTuple(curr.g + cost, new_marking, curr, (">>",t), curr.l + 1)

            heapq.heappush(open_set, tp)

        # ------ either we try to move in log
        if current_marking[1] < len(trace) :
            traversed += 1
            new_marking = (current_marking[0],current_marking[1]+1)
            if new_marking in closed.keys() :
                # if marking has already been visited, we don't visit it again
                # it's a heuristic
                continue
            queued += 1
            tp = utils.DijkstraSearchTuple(curr.g + cost_function(utils.SKIP,curr.l,expo), new_marking, curr, (trace[current_marking[1]],">>") , curr.l + 1)

            heapq.heappush(open_set, tp)

            # ------ either we try to move in both (synchronous moves)
            trans_to_visit_with_cost = [(t, cost_function(t,curr.l,expo)) for t in enabled_trans if t is not None and
                                        str(t) == trace[current_marking[1]]]
            for t, cost in trans_to_visit_with_cost:
                traversed += 1
                new_marking = (utils.add_markings(current_marking[0], t.add_marking),current_marking[1]+1)

                if new_marking in closed.keys() :
                    # if marking has already been visited, we don't visit it again
                    # it's a heuristic
                    continue

                queued += 1

                tp = utils.DijkstraSearchTuple(curr.g + cost, new_marking, curr, (trace[current_marking[1]],t), curr.l + 1)

                heapq.heappush(open_set, tp)

