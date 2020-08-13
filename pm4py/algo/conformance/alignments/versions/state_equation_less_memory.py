from pm4py.algo.conformance.alignments.versions.dijkstra_less_memory import __add_to_open_set, __add_closed, \
    __check_closed, __decode_marking, __encode_marking, __fire_trans, __dict_leq, \
    __transform_model_to_mem_efficient_structure, __transform_trace_to_mem_efficient_structure, __reconstruct_alignment, \
    get_best_worst_cost

import time
import sys
from pm4py.objects.petri import align_utils
from pm4py.objects.log import log as log_implementation
from pm4py import util as pm4pyutil
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.objects.petri.utils import construct_trace_net_cost_aware
from pm4py.objects.petri.importer import pnml as petri_importer
from pm4py.objects.petri import align_utils as utils
from pm4py.util import exec_utils
from pm4py.objects import petri
from pm4py.objects.petri.synchronous_product import construct_cost_aware
from pm4py.util.lp import solver as lp_solver
from enum import Enum
import heapq
import numpy as np
from copy import copy


class Parameters(Enum):
    PARAM_TRACE_COST_FUNCTION = 'trace_cost_function'
    PARAM_MODEL_COST_FUNCTION = 'model_cost_function'
    PARAM_STD_SYNC_COST = 'std_sync_cost'
    PARAM_MAX_ALIGN_TIME_TRACE = "max_align_time_trace"
    PARAM_MAX_ALIGN_TIME = "max_align_time"
    PARAMETER_VARIANT_DELIMITER = "variant_delimiter"
    PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE = 'ret_tuple_as_trans_desc'
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    TRACE_NET_CONSTR_FUNCTION = "trace_net_constr_function"
    TRACE_NET_COST_AWARE_CONSTR_FUNCTION = "trace_net_cost_aware_constr_function"
    PARAM_SYNC_COST_FUNCTION = 'sync_cost_function'
    PARAM_TRACE_NET_COSTS = "trace_net_costs"
    RETURN_SYNC_COST_FUNCTION = "return_sync_cost_function"


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
POSITION_HEURISTICS = 1
POSITION_INDEX = 2
POSITION_TYPE_MOVE = 3
POSITION_STATES_COUNT = 4
POSITION_PARENT_STATE = 5
POSITION_MARKING = 6
POSITION_EN_T = 7
POSITION_COST = 8
POSITION_X = 9
POSITION_TRUSTABLE = 10


def apply_from_variants_list_petri_string(var_list, petri_net_string, parameters=None):
    if parameters is None:
        parameters = {}

    petri_net, initial_marking, final_marking = petri_importer.import_petri_from_string(petri_net_string)

    res = apply_from_variants_list(var_list, petri_net, initial_marking, final_marking, parameters=parameters)
    return res


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
    dictionary: `dict` with keys **alignment**, **cost**, **visited_states**, **queued_states**
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


def construct_sync_prod_net(trace, net, im, fm, parameters=None):
    """
    Constructs the synchronous product net

    Parameters
    ---------------
    trace
        Trace
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    parameters
        Parameters

    Returns
    ----------------
    sync_prod_net
        Synchronous product net
    """
    if parameters is None:
        parameters = {}

    sync_cost = exec_utils.get_param_value(Parameters.PARAM_STD_SYNC_COST, parameters, align_utils.STD_SYNC_COST)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)
    trace_cost_function = exec_utils.get_param_value(Parameters.PARAM_TRACE_COST_FUNCTION, parameters, None)

    if trace_cost_function is None:
        trace_cost_function = list(
            map(lambda e: utils.STD_MODEL_LOG_MOVE_COST, trace))
        parameters[Parameters.PARAM_TRACE_COST_FUNCTION] = trace_cost_function

    trace_net_cost_aware_constr_function = exec_utils.get_param_value(Parameters.TRACE_NET_COST_AWARE_CONSTR_FUNCTION,
                                                                      parameters, construct_trace_net_cost_aware)
    model_cost_function = exec_utils.get_param_value(Parameters.PARAM_MODEL_COST_FUNCTION, parameters, None)

    if model_cost_function is None:
        # reset variables value
        model_cost_function = dict()
        sync_cost_function = dict()
        for t in net.transitions:
            if t.label is not None:
                model_cost_function[t] = align_utils.STD_MODEL_LOG_MOVE_COST
                sync_cost_function[t] = 0
            else:
                model_cost_function[t] = 1
        parameters[Parameters.PARAM_MODEL_COST_FUNCTION] = model_cost_function
        parameters[Parameters.PARAM_SYNC_COST_FUNCTION] = sync_cost_function

    trace_net, trace_im, trace_fm, parameters[
        Parameters.PARAM_TRACE_NET_COSTS] = trace_net_cost_aware_constr_function(trace,
                                                                                 trace_cost_function,
                                                                                 activity_key=activity_key)

    trace_net_costs = exec_utils.get_param_value(Parameters.PARAM_TRACE_NET_COSTS, parameters, None)
    if trace_net_costs is None:
        trace_net_costs = {}
        trans = sorted([(t, int(t.name.split("_")[-1])) for t in trace_net.transitions], key=lambda x: x[-1])
        for index, t in enumerate(trans):
            trace_net_costs[t[0]] = trace_cost_function[index]

    revised_sync = dict()
    for t_trace in trace_net.transitions:
        for t_model in net.transitions:
            if t_trace.label == t_model.label:
                revised_sync[(t_trace, t_model)] = sync_cost

    sync_prod, sync_initial_marking, sync_final_marking, cost_function = construct_cost_aware(
        trace_net, trace_im, trace_fm, net, im, fm, utils.SKIP,
        trace_net_costs, model_cost_function, revised_sync)

    return sync_prod, sync_final_marking, sync_final_marking, cost_function


def construct_corresp(prod_net, model_struct):
    """
    Construct the correspondency

    Parameters
    ---------------
    prod_net
        Product net
    model_struct
        Model structure

    Returns
    ---------------
    corr
        Correspondence between indexed places and places of the sync product net
    """
    sync_net = prod_net[0]
    places_dict = {x.name: y for x, y in model_struct[PLACES_DICT].items()}
    trans_dict = {y.name: x for x, y in model_struct[INV_TRANS_DICT].items()}

    corresp = [{}, {}, {}]

    for pl in sync_net.places:
        if str(pl.name[0]) != ">>":
            corresp[0][int(str(pl.name[0].split("_")[-1]))] = pl
        else:
            corresp[1][places_dict[str(pl.name[1])]] = pl

    for tr in sync_net.transitions:
        zero = str(tr.name[0])
        one = str(tr.name[1])
        if zero != ">>":
            zero = -int(zero.split("_")[-1])
        if one != ">>":
            one = trans_dict[str(tr.name[1])]
        corresp[2][(zero, one)] = tr

    return corresp


def apply(trace, net, im, fm, parameters=None):
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

    parameters = copy(parameters)
    sync_cost = exec_utils.get_param_value(Parameters.PARAM_STD_SYNC_COST, parameters, align_utils.STD_SYNC_COST)
    product_net = construct_sync_prod_net(trace, net, im, fm, parameters=parameters)

    model_struct = __transform_model_to_mem_efficient_structure(net, im, fm, parameters=parameters)
    trace_struct = __transform_trace_to_mem_efficient_structure(trace, model_struct, parameters=parameters)

    corresp = construct_corresp(product_net, model_struct)

    max_align_time_trace = exec_utils.get_param_value(Parameters.PARAM_MAX_ALIGN_TIME_TRACE, parameters,
                                                      sys.maxsize)
    ret_tuple_as_trans_desc = exec_utils.get_param_value(Parameters.PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE,
                                                         parameters, False)

    return_sync_cost = exec_utils.get_param_value(Parameters.RETURN_SYNC_COST_FUNCTION, parameters, False)
    alignment = __align(model_struct, trace_struct, product_net, corresp, sync_cost=sync_cost,
                        max_align_time_trace=max_align_time_trace,
                        ret_tuple_as_trans_desc=ret_tuple_as_trans_desc)

    if return_sync_cost:
        return alignment, product_net[3]

    return alignment


def get_corresp_marking_and_trans(m, index, corresp, t):
    marking = petri.petrinet.Marking()
    marking[corresp[0][-index]] = 1
    for pl in m:
        if not corresp[1][pl] in marking:
            marking[corresp[1][pl]] = 0
        marking[corresp[1][pl]] = marking[corresp[1][pl]] + 1
    trans = None
    if t in corresp[2]:
        trans = corresp[2][t]
    return marking, trans


def __calculate_heuristics(prev_h, prev_x, m0, index, corresp, t0, sync_net, incidence_matrix,
                           fin_vec, cost_vec, a_matrix, g_matrix, h_cvx, variant, use_cvxopt=False,
                           compute_exact_heu=False):
    """
    Calculate the heuristics

    Returns
    ---------------
    h
        Heuristic value
    x
        Solution
    """
    m, t = get_corresp_marking_and_trans(m0, index, corresp, t0)
    h = 0
    x = None

    if compute_exact_heu or t is None:
        h, x = utils.__compute_exact_heuristic_new_version(sync_net, a_matrix, h_cvx, g_matrix, cost_vec,
                                                           incidence_matrix, m, fin_vec, variant, use_cvxopt=use_cvxopt)
        trustable = True
    else:
        h, x = utils.__derive_heuristic(incidence_matrix, cost_vec, prev_x, t, prev_h)
        trustable = utils.__trust_solution(x)

    return h, x, trustable


def __align(model_struct, trace_struct, product_net, corresp, sync_cost=align_utils.STD_SYNC_COST,
            max_align_time_trace=sys.maxsize,
            ret_tuple_as_trans_desc=False):
    """
    Alignments using Dijkstra

    Parameters
    ---------------
    model_struct
        Efficient model structure
    trace_struct
        Efficient trace structure
    product_net
        Synchronous product net
    sync_cost
        Cost of a sync move (limitation: all sync moves shall have the same cost in this setting)
    corresp
        Correspondence between indexed places and places of the sync product net
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

    sync_net, ini, fin, cost_function = product_net
    incidence_matrix = petri.incidence_matrix.construct(sync_net)
    ini_vec, fin_vec, cost_vec = utils.__vectorize_initial_final_cost(incidence_matrix, ini, fin, cost_function)

    a_matrix = np.asmatrix(incidence_matrix.a_matrix).astype(np.float64)
    g_matrix = -np.eye(len(sync_net.transitions))
    h_cvx = np.matrix(np.zeros(len(sync_net.transitions))).transpose()
    cost_vec = [x * 1.0 for x in cost_vec]

    use_cvxopt = False
    if lp_solver.DEFAULT_LP_SOLVER_VARIANT == lp_solver.CVXOPT_SOLVER_CUSTOM_ALIGN or lp_solver.DEFAULT_LP_SOLVER_VARIANT == lp_solver.CVXOPT_SOLVER_CUSTOM_ALIGN_ILP:
        use_cvxopt = True

    if use_cvxopt:
        # not available in the latest version of PM4Py
        from cvxopt import matrix

        a_matrix = matrix(a_matrix)
        g_matrix = matrix(g_matrix)
        h_cvx = matrix(h_cvx)
        cost_vec = matrix(cost_vec)

    marking_dict = {}
    im = __encode_marking(marking_dict, model_struct[TRANSF_IM])
    fm = __encode_marking(marking_dict, model_struct[TRANSF_FM])

    h, x, trustable = __calculate_heuristics(None, None, im, 0, corresp, None, sync_net, incidence_matrix,
                                             fin_vec,
                                             cost_vec, a_matrix, g_matrix, h_cvx, lp_solver.DEFAULT_LP_SOLVER_VARIANT,
                                             use_cvxopt=use_cvxopt)
    exact_heu_calculations = 1

    initial_state = (0, h, 0, 0, 0, None, im, None, 0, x, trustable)
    open_set = [initial_state]
    heapq.heapify(open_set)

    closed = {}
    dummy_count = 0
    visited = 0

    while not len(open_set) == 0:
        if (time.time() - start_time) > max_align_time_trace:
            return None
        curr = heapq.heappop(open_set)
        curr_m0 = curr[POSITION_MARKING]

        curr_m = __decode_marking(curr_m0)
        index = curr[POSITION_INDEX]

        visited = visited + 1
        # if a situation equivalent to the one of the current state has been
        # visited previously, then discard this
        if __check_closed(closed, (curr_m0, curr[POSITION_INDEX])):
            continue

        h = curr[POSITION_HEURISTICS]
        x = curr[POSITION_X]
        trustable = curr[POSITION_TRUSTABLE]

        if not trustable:
            m, t = get_corresp_marking_and_trans(curr_m, index, corresp, None)
            h, x = utils.__compute_exact_heuristic_new_version(sync_net, a_matrix, h_cvx, g_matrix, cost_vec,
                                                               incidence_matrix, m, fin_vec,
                                                               lp_solver.DEFAULT_LP_SOLVER_VARIANT,
                                                               use_cvxopt=use_cvxopt)
            exact_heu_calculations = exact_heu_calculations + 1

            curr = list(curr)
            curr[POSITION_HEURISTICS] = h
            curr[POSITION_TOTAL_COST] = curr[POSITION_COST] + h
            curr[POSITION_X] = x
            curr[POSITION_TRUSTABLE] = True

            curr = tuple(curr)

            heapq.heappush(open_set, curr)
            continue

        __add_closed(closed, (curr_m0, curr[POSITION_INDEX]))
        if curr_m0 == fm:
            if -curr[POSITION_INDEX] == len(transf_trace):
                # returns the alignment only if the final marking has been reached AND
                # the trace is over
                return __reconstruct_alignment(curr, model_struct, trace_struct, visited, len(open_set), len(closed),
                                               len(marking_dict), exact_heu_calculations,
                                               ret_tuple_as_trans_desc=ret_tuple_as_trans_desc)
        # retrieves the transitions that are enabled in the current marking
        en_t = [[t, __encode_marking(marking_dict, __fire_trans(curr_m, trans_pre_dict[t], trans_post_dict[t])), 0,
                 None, False]
                for t in trans_pre_dict if __dict_leq(trans_pre_dict[t], curr_m)]

        this_closed = set()
        j = 0
        while j < len(en_t):
            t = en_t[j][0]
            # checks if a given transition can be executed in sync with the trace
            is_sync = trans_labels_dict[t] == transf_trace[-curr[POSITION_INDEX]] if -curr[POSITION_INDEX] < len(
                transf_trace) else False
            if is_sync:
                new_m = en_t[j][1]
                new_h, new_x, new_trustable = __calculate_heuristics(h, x, new_m,
                                                                     curr[POSITION_INDEX] - 1,
                                                                     corresp,
                                                                     (curr[POSITION_INDEX], t), sync_net,
                                                                     incidence_matrix,
                                                                     fin_vec,
                                                                     cost_vec, a_matrix, g_matrix, h_cvx,
                                                                     lp_solver.DEFAULT_LP_SOLVER_VARIANT,
                                                                     use_cvxopt=use_cvxopt)

                dummy_count = dummy_count + 1
                new_f = curr[POSITION_COST] + sync_cost

                new_g = new_f + new_h
                new_state = (
                    new_g, new_h, curr[POSITION_INDEX] - 1, IS_SYNC_MOVE, dummy_count,
                    curr,
                    new_m, t, new_f, new_x, new_trustable)
                if not __check_closed(closed, (new_state[POSITION_MARKING], new_state[POSITION_INDEX])):
                    # if it can be executed in a sync way, add a new state corresponding
                    # to the sync execution only if it has not already been closed
                    open_set = __add_to_open_set(open_set, new_state)
                # if a sync move reached new_m, do not schedule any model move that reaches new_m
                this_closed.add(new_m)
                del en_t[j]

                continue
            j = j + 1

        # calculate the heuristics for the remaining states
        j = 0
        while j < len(en_t):
            t = en_t[j][0]
            new_m = en_t[j][1]
            en_t[j][2], en_t[j][3], en_t[j][4] = __calculate_heuristics(h, x, new_m,
                                                                        curr[POSITION_INDEX],
                                                                        corresp, (">>", t), sync_net,
                                                                        incidence_matrix,
                                                                        fin_vec,
                                                                        cost_vec, a_matrix, g_matrix, h_cvx,
                                                                        lp_solver.DEFAULT_LP_SOLVER_VARIANT,
                                                                        use_cvxopt=use_cvxopt)
            j = j + 1

        en_t.sort(key=lambda t: transf_model_cost_function[t[0]] + t[2])
        j = 0
        while j < len(en_t):
            t = en_t[j][0]
            new_m = en_t[j][1]
            new_h = en_t[j][2]
            new_x = en_t[j][3]
            new_trustable = en_t[j][4]

            dummy_count = dummy_count + 1
            new_f = curr[POSITION_COST] + transf_model_cost_function[t]

            new_g = new_f + new_h
            new_state = (
                new_g, new_h, curr[POSITION_INDEX], IS_MODEL_MOVE,
                dummy_count, curr, new_m, t, new_f, new_x, new_trustable)
            if new_m not in this_closed and not curr_m0 == new_m:
                if not __check_closed(closed, (new_state[POSITION_MARKING], new_state[POSITION_INDEX])):
                    open_set = __add_to_open_set(open_set, new_state)
                this_closed.add(new_m)
            j = j + 1

        # IMPORTANT: to reduce the complexity, assume that you can schedule a log move
        # only if the previous move has not been a move-on-model.
        # since this setting is equivalent to scheduling all the log moves before and then
        # the model moves
        if -curr[POSITION_INDEX] < len(transf_trace) and curr[POSITION_TYPE_MOVE] != IS_MODEL_MOVE:
            dummy_count = dummy_count + 1
            new_f = curr[POSITION_COST] + trace_cost_function[-curr[POSITION_INDEX]]
            new_h, new_x, new_trustable = __calculate_heuristics(h, x, curr_m0, curr[POSITION_INDEX] - 1,
                                                                 corresp, (curr[POSITION_INDEX], ">>"), sync_net,
                                                                 incidence_matrix,
                                                                 fin_vec,
                                                                 cost_vec, a_matrix, g_matrix, h_cvx,
                                                                 lp_solver.DEFAULT_LP_SOLVER_VARIANT,
                                                                 use_cvxopt=use_cvxopt)

            new_g = new_f + new_h
            new_state = (
                new_g, new_h, curr[POSITION_INDEX] - 1,
                IS_LOG_MOVE, dummy_count, curr, curr_m0, None, new_f, new_x, new_trustable)
            if not __check_closed(closed, (new_state[POSITION_MARKING], new_state[POSITION_INDEX])):
                # adds the log move only if it has not been already closed before
                open_set = __add_to_open_set(open_set, new_state)


def __reconstruct_alignment(curr, model_struct, trace_struct, visited, open_set_length, closed_set_length,
                            num_visited_markings, exact_heu_calculations, ret_tuple_as_trans_desc=False):
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
    exact_heu_calculations
        Number of times the exact heuristics was calculated by solving an LP problem
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
    cost = curr[POSITION_COST]
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
            "closed_set_length": closed_set_length, "num_visited_markings": num_visited_markings,
            "exact_heu_calculations": exact_heu_calculations}
