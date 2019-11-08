from pm4py import util as pmutil
from pm4py.objects import log as log_lib
from pm4py.evaluation.precision import utils as precision_utils
from pm4py.objects import petri
from pm4py.objects.petri import align_utils as utils
import numpy as np
from pm4py.util.lp import factory as lp_solver_factory
import heapq

PARAM_ACTIVITY_KEY = pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY

PARAMETERS = [PARAM_ACTIVITY_KEY]


def apply(log, net, marking, final_marking, parameters=None):
    """
    Get Align-ET Conformance precision

    Parameters
    ----------
    log
        Trace log
    net
        Petri net
    marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm, including:
            pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> Activity key
    """

    if parameters is None:
        parameters = {}

    activity_key = parameters[
        PARAM_ACTIVITY_KEY] if PARAM_ACTIVITY_KEY in parameters else log_lib.util.xes.DEFAULT_NAME_KEY
    precision = 0.0
    sum_ee = 0
    sum_at = 0

    if not (petri.check_soundness.check_wfnet(net) and petri.check_soundness.check_relaxed_soundness_net_in_fin_marking(net,
                                                                                                            marking,
                                                                                                            final_marking)):
        raise Exception("trying to apply Align-ETConformance on a Petri net that is not a relaxed sound workflow net!!")

    prefixes, prefix_count = precision_utils.get_log_prefixes(log, activity_key=activity_key)
    prefixes_keys = list(prefixes.keys())
    fake_log = precision_utils.form_fake_log(prefixes_keys, activity_key=activity_key)

    align_stop_marking = align_fake_log_stop_marking(fake_log, net, marking, final_marking, parameters=parameters)
    all_markings = transform_markings_from_sync_to_original_net(align_stop_marking, net, parameters=parameters)

    for i in range(len(all_markings)):
        atm = all_markings[i]

        log_transitions = set(prefixes[prefixes_keys[i]])
        activated_transitions_labels = set(x.label for x in utils.get_visible_transitions_eventually_enabled_by_marking(net, atm) if x.label is not None)
        sum_at += len(activated_transitions_labels) * prefix_count[prefixes_keys[i]]
        escaping_edges = activated_transitions_labels.difference(log_transitions)
        sum_ee += len(escaping_edges) * prefix_count[prefixes_keys[i]]

    if sum_at > 0:
        precision = 1 - float(sum_ee) / float(sum_at)

    return precision


def transform_markings_from_sync_to_original_net(markings0, net, parameters=None):
    """
    Transform the markings of the sync net (in which alignment stops) into markings of the original net
    (in order to measure the precision)

    Parameters
    -------------
    markings0
        Markings on the sync net (expressed as place name with count)
    net
        Petri net
    parameters
        Parameters of the Petri net

    Returns
    -------------
    markings
        Markings of the original model (expressed as place with count)
    """
    if parameters is None:
        parameters = {}

    places_corr = {p.name:p for p in net.places}

    markings = []

    for i in range(len(markings0)):
        res = markings0[i]
        atm = petri.petrinet.Marking()
        for pl, count in res.items():
            if pl[0] == utils.SKIP:
                atm[places_corr[pl[1]]] = count
        markings.append(atm)

    return markings

def align_fake_log_stop_marking(fake_log, net, marking, final_marking, parameters=None):
    """
    Align the 'fake' log with all the prefixes in order to get the markings in which
    the alignment stops

    Parameters
    -------------
    fake_log
        Fake log
    net
        Petri net
    marking
        Marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm

    Returns
    -------------
    alignment
        For each trace in the log, return the marking in which the alignment stops (expressed as place name with count)
    """
    if parameters is None:
        parameters = {}
    max_trace_length = max(len(x) for x in fake_log)
    align_result = []
    for i in range(len(fake_log)):
        trace = fake_log[i]
        sync_net, sync_initial_marking, sync_final_marking = build_sync_net(trace, net, marking, final_marking)
        stop_marking = petri.petrinet.Marking()
        for pl, count in sync_final_marking.items():
            if pl.name[1] == utils.SKIP:
                stop_marking[pl] = count
        cost_function = utils.construct_standard_cost_function(sync_net, utils.SKIP)

        res = __search(sync_net, sync_initial_marking, sync_final_marking, stop_marking, cost_function, utils.SKIP, max_trace_length)
        res2 = {}

        for pl in res:
            res2[(pl.name[0], pl.name[1])] = res[pl]

        align_result.append(res2)

    return align_result

def build_sync_net(trace, petri_net, initial_marking, final_marking, parameters=None):
    """
    Build the sync product net between the Petri net and the trace prefix

    Parameters
    ---------------
    trace
        Trace prefix
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Possible parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[
        PARAM_ACTIVITY_KEY] if PARAM_ACTIVITY_KEY in parameters else log_lib.util.xes.DEFAULT_NAME_KEY

    trace_net, trace_im, trace_fm = petri.utils.construct_trace_net(trace, activity_key=activity_key)

    sync_prod, sync_initial_marking, sync_final_marking = petri.synchronous_product.construct(trace_net, trace_im,
                                                                                              trace_fm, petri_net,
                                                                                              initial_marking,
                                                                                              final_marking,
                                                                                              utils.SKIP)

    return sync_prod, sync_initial_marking, sync_final_marking


def __search(sync_net, ini, fin, stop, cost_function, skip, max_trace_length):
    from pm4py.objects.petri.utils import decorate_places_preset_trans, decorate_transitions_prepostset

    decorate_transitions_prepostset(sync_net)
    decorate_places_preset_trans(sync_net)

    incidence_matrix = petri.incidence_matrix.construct(sync_net)
    ini_vec, fin_vec, cost_vec = utils.__vectorize_initial_final_cost(incidence_matrix, ini, fin, cost_function)

    closed = set()

    a_matrix = np.asmatrix(incidence_matrix.a_matrix).astype(np.float64)
    g_matrix = -np.eye(len(sync_net.transitions))
    h_cvx = np.matrix(np.zeros(len(sync_net.transitions))).transpose()
    cost_vec = [x * 1.0 for x in cost_vec]

    use_cvxopt = False
    if lp_solver_factory.DEFAULT_LP_SOLVER_VARIANT == lp_solver_factory.CVXOPT_SOLVER_CUSTOM_ALIGN or lp_solver_factory.DEFAULT_LP_SOLVER_VARIANT == lp_solver_factory.CVXOPT_SOLVER_CUSTOM_ALIGN_ILP:
        use_cvxopt = True

    if use_cvxopt:
        # not available in the latest version of PM4Py
        from cvxopt import matrix

        a_matrix = matrix(a_matrix)
        g_matrix = matrix(g_matrix)
        h_cvx = matrix(h_cvx)
        cost_vec = matrix(cost_vec)

    h, x = utils.__compute_exact_heuristic_new_version(sync_net, a_matrix, h_cvx, g_matrix, cost_vec, incidence_matrix, ini,
                                                 fin_vec, lp_solver_factory.DEFAULT_LP_SOLVER_VARIANT, use_cvxopt=use_cvxopt)
    # heuristics need to be adapted for prefix alignments
    # here we make the heuristics way less powerful
    h = h / (max_trace_length + 1.0)
    ini_state = utils.SearchTuple(0 + h, 0, h, ini, None, None, x, True)
    open_set = [ini_state]
    heapq.heapify(open_set)
    visited = 0
    queued = 0
    traversed = 0
    while not len(open_set) == 0:
        curr = heapq.heappop(open_set)

        current_marking = curr.m
        # 11/10/2019 (optimization Y, that was optimization X,
        # but with the good reasons this way): avoid checking markings in the cycle using
        # the __get_alt function, but check them 'on the road'
        already_closed = current_marking in closed
        if already_closed:
            continue

        while not curr.trust:
            h, x = utils.__compute_exact_heuristic_new_version(sync_net, a_matrix, h_cvx, g_matrix, cost_vec,
                                                         incidence_matrix, curr.m,
                                                         fin_vec, lp_solver_factory.DEFAULT_LP_SOLVER_VARIANT, use_cvxopt=use_cvxopt)
            # heuristics need to be adapted for prefix alignments
            # here we make the heuristics way less powerful
            h = h / (max_trace_length + 1.0)

            # 11/10/19: shall not a state for which we compute the exact heuristics be
            # by nature a trusted solution?
            tp = utils.SearchTuple(curr.g + h, curr.g, h, curr.m, curr.p, curr.t, x, True)
            # 11/10/2019 (optimization ZA) heappushpop is slightly more efficient than pushing
            # and popping separately
            curr = heapq.heappushpop(open_set, tp)
            current_marking = curr.m

        # max allowed heuristics value (27/10/2019, due to the numerical instability of some of our solvers)
        if curr.h > lp_solver_factory.MAX_ALLOWED_HEURISTICS:
            continue

        # 12/10/2019: do it again, since the marking could be changed
        already_closed = current_marking in closed
        if already_closed:
            continue

        # 12/10/2019: the current marking can be equal to the final marking only if the heuristics
        # (underestimation of the remaining cost) is 0. Low-hanging fruits
        if stop <= current_marking:
            return current_marking
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
            h, x = utils.__derive_heuristic(incidence_matrix, cost_vec, curr.x, t, curr.h)
            # heuristics need to be adapted for prefix alignments
            # here we make the heuristics way less powerful
            h = h / (max_trace_length + 1.0)

            trustable = utils.__trust_solution(x)
            new_f = g + h

            tp = utils.SearchTuple(new_f, g, h, new_marking, curr, t, x, trustable)
            heapq.heappush(open_set, tp)
