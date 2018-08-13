from pm4py.models import petri
from pm4py.algo import alignments as alignments_lib
from pm4py import log as log_lib
import numpy as np
import heapq
from dataclasses import dataclass, field
from typing import Any
from cvxopt import matrix, solvers
import datetime
from multiprocessing import Pool, Manager
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


def apply_trace(trace, petri_net, initial_marking, final_marking):
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
    trace_net, trace_im, trace_fm = petri.utils.construct_trace_net(trace)
    sync_prod, sync_initial_marking, sync_final_marking = petri.synchronous_product.construct(trace_net, trace_im,
                                                                                              trace_fm, petri_net,
                                                                                              initial_marking,
                                                                                              final_marking,
                                                                                              alignments_lib.utils.SKIP)
    cost_function = alignments_lib.utils.construct_standard_cost_function(sync_prod, alignments_lib.utils.SKIP)
    return apply_sync_prod(sync_prod, sync_initial_marking, sync_final_marking, cost_function, alignments_lib.utils.SKIP)



def __apply_trace_best_worst_known(trace, petri_net, initial_marking, final_marking, best_worst):
    trace_net, trace_im, trace_fm = petri.utils.construct_trace_net(trace)
    sync_prod, sync_initial_marking, sync_final_marking = petri.synchronous_product.construct(trace_net, trace_im, trace_fm, petri_net, initial_marking, final_marking, alignments_lib.utils.SKIP)
    cost_function = alignments_lib.utils.construct_standard_cost_function(sync_prod, alignments_lib.utils.SKIP)
    alignment = __search(sync_prod, sync_initial_marking, sync_final_marking, cost_function, alignments_lib.utils.SKIP)
    fixed_costs = alignment['cost'] //  alignments_lib.utils.STD_MODEL_LOG_MOVE_COST
    fitness = 1 - (fixed_costs / best_worst )
    return {'trace': trace, 'alignment': alignment['alignment'], 'costs': fixed_costs, 'fitness':fitness, 'visited_states': alignment['visited_states'], 'queued_states': alignment['queued_states'], 'traversed_arcs': alignment['traversed_arcs'] }


def apply_log(log, petri_net, initial_marking, final_marking):
    best_worst = apply_trace(log_lib.instance.Trace(), petri_net, initial_marking, final_marking)
    best_worst_costs = best_worst['cost'] // alignments_lib.utils.STD_MODEL_LOG_MOVE_COST
    with Pool(max(1, mp.cpu_count() - 1)) as pool: 
        return pool.starmap(__apply_trace_best_worst_known, map(lambda tr: (tr, petri_net, initial_marking, final_marking, best_worst_costs), log))


def __search(sync_net, ini, fin, cost_function, skip):
    incidence_matrix = petri.incidence_matrix.construct(sync_net)
    ini_vec, fin_vec, cost_vec = __vectorize_initial_final_cost(incidence_matrix, ini, fin, cost_function)

    closed = set()
    h, x = __compute_exact_heuristic(sync_net, incidence_matrix, ini, cost_vec, fin_vec, [0], None, 0)
    shadow_map = dict()
    ini_state = SearchTuple(0+h, 0, h, ini, None, None, x)
    open_set = [ini_state]
    shadow_map[ini] = ini_state
    visited = 0
    queued = 0
    traversed = 0
    while not len(open_set) == 0:
        curr = heapq.heappop(open_set)
        visited += 1
        current_marking = curr.m
        closed.add(current_marking)
        if current_marking == fin:
            parent = curr.p
            alignment = [curr.t.label]
            while parent.p is not None:
                alignment = [parent.t.label] + alignment
                parent = parent.p
            return {'alignment': alignment, 'cost': curr.g, 'visited_states': visited, 'queued_states': queued, 'traversed_arcs': traversed}

        prev_t = curr.t
        for t in petri.semantics.enabled_transitions(sync_net, current_marking):
            if prev_t is not None and prev_t.label[0] != skip and prev_t.label[1] == skip and t.label[0] == skip and (t.label[1] != skip or t.label[1] is None):
                continue
            traversed += 1
            new_marking = petri.semantics.execute(t, sync_net, current_marking)
            #if __get_eq_marking_from_set(new_marking, closed) is not None:
            if new_marking in closed:
                continue
            g = curr.g + cost_function[t]

            # shadow = __get_tuple_from_queue(new_marking, open_set)
            shadow = shadow_map[new_marking] if new_marking in shadow_map else None
            if shadow is not None:
                if g >= shadow.g:
                    continue
                h = shadow.h
                open_set.remove(shadow)
            else:
                queued += 1
                h, x = __compute_exact_heuristic(sync_net, incidence_matrix, ini, cost_vec, fin_vec, curr.x, t, curr.h)

            tp = SearchTuple(g+h, g, h, new_marking, curr, t, x)
            shadow_map[new_marking] = tp
            heapq.heappush(open_set, tp)
            heapq.heapify(open_set)


def __compute_exact_heuristic(sync_net, incidence_matrix, new_marking, cost_vec, fin_vec, x, t, h):
    '''
    Computes an exact heuristic using an LP based on the marking equation.

    Parameters
    ----------
    :param sync_net: synchronous product net
    :param incidence_matrix: incidence matrix
    :param new_marking: marking to start from
    :param cost_vec: cost vector
    :param fin_vec: marking to reach

    Returns
    -------
    :return: h: heuristic value, x: solution vector
    '''
    if t is not None:
        x_prime = x.copy()
        x_prime[incidence_matrix.transitions[t]] -= 1
        if x_prime[incidence_matrix.transitions[t]] >= 0:
            return h - cost_vec[incidence_matrix.transitions[t]], x_prime

    m_vec = incidence_matrix.encode_marking(new_marking)
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


def __get_eq_marking_from_set(marking, marking_map):
    start = datetime.datetime.now()
    for m in marking_map:
        if m == marking:
            if (datetime.datetime.now() - start).microseconds > 0:
                print('search', (datetime.datetime.now() - start).microseconds)
            return m
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
    g: float = field(compare=False)
    h: float = field(compare=False)
    m: petri.net.Marking = field(compare=False)
    p: Any = field(compare=False)
    t: petri.net.PetriNet.Transition = field(compare=False)
    x: Any = field(compare=False)

    def __lt__(self, other):
        if self.f == other.f:
            return self.h < other.h
        return self.f < other.f

    def __get_firing_sequence(self):
        ret = []
        if self.p is not None:
            ret = ret + self.p.__get_firing_sequence()
        if self.t is not None:
            ret.append(self.t)
        return ret

    def __repr__(self):
        stringBuild = []
        stringBuild.append("\nmarking=" + str(self.m))
        stringBuild.append(" totalCost=" + str(self.f))
        stringBuild.append(" heuristic=" + str(self.h))
        stringBuild.append(" allActivatedTransitions=" + str(self.__get_firing_sequence()) + "\n\n")
        return " ".join(stringBuild)
