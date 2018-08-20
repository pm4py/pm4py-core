from pm4py.models import petri
from pm4py.algo import alignments as alignments_lib
from pm4py import log as log_lib
import numpy as np
import heapq
from dataclasses import dataclass, field
from typing import Any
from cvxopt import matrix, solvers
import datetime
from multiprocessing import Pool
import multiprocessing as mp


def apply_sync_prod(sync_prod, ini, fin, cost, skip):
    '''
    Performs the basic alignment search on top of the synchronous product net, given a cost function and skyp-symbol

    Parameters
    ----------
    :param sync_prod: synchronous product net
    :param ini: initial marking in the synchronous product net
    :param fin: final marking in the synchronous product net
    :param cost: cost function mapping transitions to the synchronous product net
    :param skip: symbol to use for skips in the alignment

    Returns
    -------
    :return: dict with keys: alignment, cost, visited_states, queued_states and traversed_arcs
    '''
    return __search(sync_prod, ini, fin, cost, skip)


def apply_trace(trace, petri_net, initial_marking, final_marking, activity_key="concept:name"):
    '''
    Performs the basic alignment search, given a trace and a net

    Parameters
    ----------
    :param trace:
    :param petri_net:
    :param initial_marking:
    :param final_marking:

    Returns
    -------
    :return:dict with keys: alignment, cost, visited_states, queued_states and traversed_arcs
    '''
    trace_net, trace_im, trace_fm = petri.utils.construct_trace_net(trace, activity_key=activity_key)
    sync_prod, sync_initial_marking, sync_final_marking = petri.synchronous_product.construct(trace_net, trace_im,
                                                                                              trace_fm, petri_net,
                                                                                              initial_marking,
                                                                                              final_marking,
                                                                                              alignments_lib.utils.SKIP)
    cost_function = alignments_lib.utils.construct_standard_cost_function(sync_prod, alignments_lib.utils.SKIP)
    return apply_sync_prod(sync_prod, sync_initial_marking, sync_final_marking, cost_function, alignments_lib.utils.SKIP)


def __apply_trace_best_worst_known(trace, petri_net, initial_marking, final_marking, best_worst, activity_key="concept:name"):
    trace_net, trace_im, trace_fm = petri.utils.construct_trace_net(trace, activity_key=activity_key)
    sync_prod, sync_initial_marking, sync_final_marking = petri.synchronous_product.construct(trace_net, trace_im, trace_fm, petri_net, initial_marking, final_marking, alignments_lib.utils.SKIP)
    cost_function = alignments_lib.utils.construct_standard_cost_function(sync_prod, alignments_lib.utils.SKIP)
    alignment = __search(sync_prod, sync_initial_marking, sync_final_marking, cost_function, alignments_lib.utils.SKIP)
    fixed_costs = alignment['cost'] //  alignments_lib.utils.STD_MODEL_LOG_MOVE_COST
    fitness = 1 - (fixed_costs / best_worst )
    return {'trace': trace, 'alignment': alignment['alignment'], 'cost': fixed_costs, 'fitness':fitness, 'visited_states': alignment['visited_states'], 'queued_states': alignment['queued_states'], 'traversed_arcs': alignment['traversed_arcs'] }


def apply_log(log, petri_net, initial_marking, final_marking, activity_key="concept:name"):
    best_worst = apply_trace(log_lib.instance.Trace(), petri_net, initial_marking, final_marking)
    best_worst_costs = best_worst['cost'] // alignments_lib.utils.STD_MODEL_LOG_MOVE_COST
    with Pool(max(1, mp.cpu_count() - 1)) as pool: 
        return pool.starmap(__apply_trace_best_worst_known, map(lambda tr: (tr, petri_net, initial_marking, final_marking, best_worst_costs, activity_key), log))


def __search(sync_net, ini, fin, cost_function, skip):
    incidence_matrix = petri.incidence_matrix.construct(sync_net)
    ini_vec, fin_vec, cost_vec = __vectorize_initial_final_cost(incidence_matrix, ini, fin, cost_function)

    closed = set()
    h, x = __compute_exact_heuristic(sync_net, incidence_matrix, ini, cost_vec, fin_vec)
    ini_state = SearchTuple(0+h, 0, h, ini, None, None, x, True)
    open_set = [ini_state]
    visited = 0
    queued = 0
    traversed = 0
    while not len(open_set) == 0:
        curr = heapq.heappop(open_set)
        if not curr.trust:
            h, x = __compute_exact_heuristic(sync_net, incidence_matrix, curr.m, cost_vec, fin_vec)
            tp = SearchTuple(curr.g + h, curr.g, h, curr.m, curr.p, curr.t, x, __trust_solution(x))
            heapq.heappush(open_set, tp)
            heapq.heapify(open_set)
            continue

        visited += 1
        current_marking = curr.m
        closed.add(current_marking)
        if current_marking == fin:
            return __reconstruct_alignment(curr, visited, queued, traversed)
        for t in petri.semantics.enabled_transitions(sync_net, current_marking):
            if curr.t is not None and __is_log_move(curr.t, skip) and __is_model_move(t, skip):
                continue
            traversed += 1
            new_marking = petri.semantics.execute(t, sync_net, current_marking)
            if new_marking in closed:
                continue
            g = curr.g + cost_function[t]

            alt = next((enum[1] for enum in enumerate(open_set) if enum[1].m == new_marking), None)
            if alt is not None:
                if g >= alt.g:
                    continue
                open_set.remove(alt)
                heapq.heapify(open_set)
            queued += 1
            h, x = __derive_heuristic(incidence_matrix, cost_vec, curr.x, t, curr.h)
            tp = SearchTuple(g+h, g, h, new_marking, curr, t, x, __trust_solution(x))
            heapq.heappush(open_set, tp)
            heapq.heapify(open_set)


def __reconstruct_alignment(state, visited, queued, traversed):
    parent = state.p
    alignment = [state.t.label]
    while parent.p is not None:
        alignment = [parent.t.label] + alignment
        parent = parent.p
    return {'alignment': alignment, 'cost': state.g, 'visited_states': visited, 'queued_states': queued,
            'traversed_arcs': traversed}


def __derive_heuristic(incidence_matrix, cost_vec, x, t, h):
    x_prime = x.copy()
    x_prime[incidence_matrix.transitions[t]] -= 1
    return max(0, h - cost_vec[incidence_matrix.transitions[t]]), x_prime


def __is_model_move(t, skip):
    return t.label[0] == skip and t.label[1] != skip


def __is_log_move(t, skip):
    return t.label[0] != skip and t.label[1] == skip


def __trust_solution(x):
    for v in x:
        if v < -0.001:
            return False
    return True


def __compute_exact_heuristic(sync_net, incidence_matrix, marking, cost_vec, fin_vec):
    '''
    Computes an exact heuristic using an LP based on the marking equation.

    Parameters
    ----------
    :param sync_net: synchronous product net
    :param incidence_matrix: incidence matrix
    :param marking: marking to start from
    :param cost_vec: cost vector
    :param fin_vec: marking to reach

    Returns
    -------
    :return: h: heuristic value, x: solution vector
    '''
    m_vec = incidence_matrix.encode_marking(marking)
    G = matrix(-np.eye(len(sync_net.transitions)))
    h_cvx = matrix(np.zeros(len(sync_net.transitions)))
    A = matrix(incidence_matrix.A, tc='d')
    h_obj = solvers.lp(matrix(cost_vec, tc='d'), G, h_cvx, A.trans(),
                       matrix([i - j for i, j in zip(fin_vec, m_vec)], tc='d'), solver='glpk',
                       options={'glpk': {'msg_lev': 'GLP_MSG_OFF'}})
    h = h_obj['primal objective']
    return h, [xi for xi in h_obj['x']]


def __get_tuple_from_queue(marking, queue):
    for t in queue:
        if t.m == marking:
            return t
    return None


def __vectorize_initial_final_cost(incidence_matrix, ini, fin, cost_function):
    ini_vec = incidence_matrix.encode_marking(ini)
    fini_vec = incidence_matrix.encode_marking(fin)
    cost_vec = [0] * len(cost_function)
    for t in cost_function.keys():
        cost_vec[incidence_matrix.transitions[t]] = cost_function[t]
    return ini_vec, fini_vec, cost_vec


@dataclass
class SearchTuple:
    f: float
    g: float
    h: float
    m: petri.net.Marking
    p: Any
    t: petri.net.PetriNet.Transition
    x: Any
    trust: bool

    def __lt__(self, other):
        if self.f < other.f:
            return True
        elif other.f < self.f:
            return False
        else:
            if self.trust == other.trust:
                if self.h < other.h:
                    return True
                else:
                    return False
            else:
                return self.trust

    def __get_firing_sequence(self):
        ret = []
        if self.p is not None:
            ret = ret + self.p.__get_firing_sequence()
        if self.t is not None:
            ret.append(self.t)
        return ret

    def __repr__(self):
        stringBuild = []
        stringBuild.append("\nm=" + str(self.m))
        stringBuild.append(" f=" + str(self.f))
        stringBuild.append(' g=' + str(self.g))
        stringBuild.append(" h=" + str(self.h))
        stringBuild.append(" path=" + str(self.__get_firing_sequence()) + "\n\n")
        return " ".join(stringBuild)
