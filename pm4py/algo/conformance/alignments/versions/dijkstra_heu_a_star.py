import heapq
import sys
from copy import copy
import time

import numpy as np

import pm4py
from pm4py import util as pm4pyutil
from pm4py.objects import petri
from pm4py.objects.petri.importer import pnml as petri_importer
from pm4py.objects.log import log as log_implementation
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.objects.petri.synchronous_product import construct_cost_aware
from pm4py.objects.petri.utils import construct_trace_net_cost_aware, decorate_places_preset_trans, decorate_transitions_prepostset
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.objects.petri import align_utils as utils
import networkx as nx
from pm4py.objects.petri import networkx_graph

PARAM_TRACE_COST_FUNCTION = 'trace_cost_function'
PARAM_MODEL_COST_FUNCTION = 'model_cost_function'
PARAM_SYNC_COST_FUNCTION = 'sync_cost_function'

PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE = 'ret_tuple_as_trans_desc'
PARAM_TRACE_NET_COSTS = "trace_net_costs"

TRACE_NET_CONSTR_FUNCTION = "trace_net_constr_function"
TRACE_NET_COST_AWARE_CONSTR_FUNCTION = "trace_net_cost_aware_constr_function"

PARAM_MAX_ALIGN_TIME_TRACE = "max_align_time_trace"
DEFAULT_MAX_ALIGN_TIME_TRACE = sys.maxsize
PARAM_MAX_ALIGN_TIME = "max_align_time"
DEFAULT_MAX_ALIGN_TIME = sys.maxsize

PARAMETER_VARIANT_DELIMITER = "variant_delimiter"
DEFAULT_VARIANT_DELIMITER = ","

PARAMETERS = [PARAM_TRACE_COST_FUNCTION, PARAM_MODEL_COST_FUNCTION, PARAM_SYNC_COST_FUNCTION,
              pm4pyutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]

def get_best_worst_cost(petri_net, initial_marking, final_marking, parameters=None):
    trace = log_implementation.Trace()
    new_parameters = copy(parameters)
    if PARAM_TRACE_COST_FUNCTION not in new_parameters or len(new_parameters[PARAM_TRACE_COST_FUNCTION]) < len(trace):
        new_parameters[PARAM_TRACE_COST_FUNCTION] = list(
            map(lambda e: utils.STD_MODEL_LOG_MOVE_COST, trace))

    best_worst = pm4py.algo.conformance.alignments.versions.state_equation_a_star.apply(trace,
                                                                                        petri_net, initial_marking,
                                                                                        final_marking,
                                                                                        parameters=new_parameters)

    if best_worst['cost'] > 0:
        return best_worst['cost'] // utils.STD_MODEL_LOG_MOVE_COST
    return 0

def apply(trace, petri_net, initial_marking, final_marking, parameters=None):
    if parameters is None:
        parameters = {}

    activity_key = DEFAULT_NAME_KEY if parameters is None or PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters else \
        parameters[
            pm4pyutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    if parameters is None or PARAM_TRACE_COST_FUNCTION not in parameters or PARAM_MODEL_COST_FUNCTION not in parameters or PARAM_SYNC_COST_FUNCTION not in parameters:
        trace_net_constr_function = parameters[
            TRACE_NET_CONSTR_FUNCTION] if TRACE_NET_CONSTR_FUNCTION in parameters else petri.utils.construct_trace_net
        trace_net, trace_im, trace_fm = trace_net_constr_function(trace, activity_key=activity_key)

    else:
        trace_net_cost_aware_constr_function = parameters[
            TRACE_NET_COST_AWARE_CONSTR_FUNCTION] if TRACE_NET_COST_AWARE_CONSTR_FUNCTION in parameters else construct_trace_net_cost_aware
        trace_net, trace_im, trace_fm, parameters[PARAM_TRACE_NET_COSTS] = trace_net_cost_aware_constr_function(trace,
                                                                                                                parameters[
                                                                                                                    PARAM_TRACE_COST_FUNCTION],
                                                                                                                activity_key=activity_key)

    return apply_trace_net(petri_net, initial_marking, final_marking, trace_net, trace_im, trace_fm, parameters)


def apply_from_variant(variant, petri_net, initial_marking, final_marking, parameters=None):
    if parameters is None:
        parameters = {}
    activity_key = DEFAULT_NAME_KEY if parameters is None or PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters else \
        parameters[
            pm4pyutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    trace = log_implementation.Trace()
    variant_delimiter = parameters[
        PARAMETER_VARIANT_DELIMITER] if PARAMETER_VARIANT_DELIMITER in parameters else DEFAULT_VARIANT_DELIMITER
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
    if parameters is None:
        parameters = {}
    start_time = time.time()
    max_align_time = parameters[PARAM_MAX_ALIGN_TIME] if PARAM_MAX_ALIGN_TIME in parameters else DEFAULT_MAX_ALIGN_TIME
    max_align_time_case = parameters[
        PARAM_MAX_ALIGN_TIME_TRACE] if PARAM_MAX_ALIGN_TIME_TRACE in parameters else DEFAULT_MAX_ALIGN_TIME_TRACE
    dictio_alignments = {}
    for varitem in var_list:
        this_max_align_time = min(max_align_time_case, (max_align_time - (time.time() - start_time)) * 0.5)
        variant = varitem[0]
        parameters[PARAM_MAX_ALIGN_TIME_TRACE] = this_max_align_time
        dictio_alignments[variant] = apply_from_variant(variant, petri_net, initial_marking, final_marking,
                                                        parameters=parameters)
    return dictio_alignments


def apply_from_variants_list_petri_string(var_list, petri_net_string, parameters=None):
    if parameters is None:
        parameters = {}

    petri_net, initial_marking, final_marking = petri_importer.import_petri_from_string(petri_net_string)

    res = apply_from_variants_list(var_list, petri_net, initial_marking, final_marking, parameters=parameters)
    return res


def apply_from_variants_list_petri_string_mprocessing(mp_output, var_list, petri_net_string, parameters=None):
    if parameters is None:
        parameters = {}

    res = apply_from_variants_list_petri_string(var_list, petri_net_string, parameters=parameters)
    mp_output.put(res)


def apply_trace_net(petri_net, initial_marking, final_marking, trace_net, trace_im, trace_fm, parameters=None):
    ret_tuple_as_trans_desc = parameters[
        PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE] if PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE in parameters else False

    if parameters is None or PARAM_TRACE_COST_FUNCTION not in parameters or PARAM_MODEL_COST_FUNCTION not in parameters or PARAM_SYNC_COST_FUNCTION not in parameters:
        sync_prod, sync_initial_marking, sync_final_marking = petri.synchronous_product.construct(trace_net, trace_im,
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
                    revised_sync[(t_trace, t_model)] = parameters[PARAM_SYNC_COST_FUNCTION][t_model]

        sync_prod, sync_initial_marking, sync_final_marking, cost_function = construct_cost_aware(
            trace_net, trace_im, trace_fm, petri_net, initial_marking, final_marking, utils.SKIP,
            parameters[PARAM_TRACE_NET_COSTS], parameters[PARAM_MODEL_COST_FUNCTION], revised_sync)

    max_align_time_trace = parameters[
        PARAM_MAX_ALIGN_TIME_TRACE] if PARAM_MAX_ALIGN_TIME_TRACE in parameters else DEFAULT_MAX_ALIGN_TIME_TRACE

    return apply_sync_prod(sync_prod, sync_initial_marking, sync_final_marking, cost_function,
                           utils.SKIP, ret_tuple_as_trans_desc=ret_tuple_as_trans_desc,
                           max_align_time_trace=max_align_time_trace)


def apply_sync_prod(sync_prod, initial_marking, final_marking, cost_function, skip, ret_tuple_as_trans_desc=False,
                    max_align_time_trace=DEFAULT_MAX_ALIGN_TIME_TRACE):
    return __search(sync_prod, initial_marking, final_marking, cost_function, skip,
                    ret_tuple_as_trans_desc=ret_tuple_as_trans_desc, max_align_time_trace=max_align_time_trace)


def get_map_pla_spaths(sync_net, cost_function, fin):
    G, inv_dictionary = networkx_graph.create_networkx_directed_graph(sync_net, weight=cost_function)
    dictionary = {y:x for x,y in inv_dictionary.items()}
    map_all_spaths = nx.algorithms.shortest_paths.shortest_path(G, weight="weight")
    map_pla_spaths = {}
    for p1 in sync_net.places:
        all_spaths = [[inv_dictionary[x] for x in map_all_spaths[dictionary[p1]][dictionary[p2]]] for p2 in fin if dictionary[p2] in map_all_spaths[dictionary[p1]]]
        all_spaths = [[y for y in x if type(y) is petri.petrinet.PetriNet.Transition] for x in all_spaths]
        map_pla_spaths[p1] = min(sum(cost_function[y] for y in x) for x in all_spaths) if all_spaths else sys.maxsize

    return map_pla_spaths


def __search(sync_net, ini, fin, cost_function, skip, ret_tuple_as_trans_desc=False,
             max_align_time_trace=DEFAULT_MAX_ALIGN_TIME_TRACE):
    start_time = time.time()

    decorate_transitions_prepostset(sync_net)
    decorate_places_preset_trans(sync_net)

    map_pla_spaths = get_map_pla_spaths(sync_net, cost_function, fin)

    closed = set()

    x = None
    h = max(map_pla_spaths[pp] for pp in ini)

    ini_state = utils.SearchTuple(0 + h, 0, h, ini, None, None, x, True)
    open_set = [ini_state]
    heapq.heapify(open_set)
    visited = 0
    queued = 0
    traversed = 0
    while not len(open_set) == 0:
        if (time.time() - start_time) > max_align_time_trace:
            return None

        curr = heapq.heappop(open_set)

        current_marking = curr.m
        already_closed = current_marking in closed
        if already_closed:
            continue

        if current_marking == fin:
            return utils.__reconstruct_alignment(curr, visited, queued, traversed,
                                           ret_tuple_as_trans_desc=ret_tuple_as_trans_desc)

        closed.add(current_marking)
        visited += 1

        possible_enabling_transitions = set()
        for p in current_marking:
            for t in p.ass_trans:
                possible_enabling_transitions.add(t)

        enabled_trans = [t for t in possible_enabling_transitions if t.sub_marking <= current_marking]

        trans_to_visit_with_cost = [(t, cost_function[t]) for t in enabled_trans if not (
                curr.t is not None and utils.__is_log_move(curr.t, skip) and utils.__is_model_move(t, skip))]

        for t, cost in trans_to_visit_with_cost:
            traversed += 1
            new_marking = utils.add_markings(current_marking, t.add_marking)

            if new_marking in closed:
                continue
            g = curr.g + cost

            queued += 1
            h = max(map_pla_spaths[pp] for pp in curr.m)

            new_f = g + h

            tp = utils.SearchTuple(new_f, g, h, new_marking, curr, t, x, True)
            heapq.heappush(open_set, tp)
