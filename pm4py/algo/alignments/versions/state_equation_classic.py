from pm4py.models import petri
from pm4py.algo import alignments
import numpy as np
import scipy.optimize as sp
import time
import heapq
from dataclasses import dataclass, field
from typing import Any


def apply_log(log, petri_net, initial_marking, final_marking):
    alignments = []
    for t in log:
        alignments.append(apply_trace(t, petri_net, initial_marking, final_marking))
    return alignments


def apply_trace(trace, petri_net, initial_marking, final_marking):
    trace_net, trace_im, trace_fm = petri.utils.construct_trace_net(trace)
    sync_prod, sync_initial_marking, sync_final_marking = petri.synchronous_product.construct(trace_net, trace_im, trace_fm, petri_net, initial_marking, final_marking, alignments.utils.SKIP)
    cost_function = alignments.utils.construct_standard_cost_function(sync_prod, alignments.utils.SKIP)
    alignment = __search(sync_prod, sync_initial_marking, sync_final_marking, cost_function)
    return alignment


def __search(sync_net, ini, fin, cost_function):
    incidence_matrix = petri.incidence_matrix.construct(sync_net)
    ini_vec, fin_vec, cost_vec = __vectorize_initial_final_cost(incidence_matrix,ini,fin,cost_function)

    closed = set()
    ini_state = SearchTuple(0, 0, 0, ini, None, None)
    marking_map = {ini: ini_state}
    open_set = [ini_state]
    while not len(open_set) == 0:
        curr = heapq.heappop(open_set)
        current_marking = curr.m
        del marking_map[current_marking]
        closed.add(current_marking)
        if current_marking == fin:
            parent = curr.p
            alignment = [curr.t]
            while parent.p is not None:
                alignment = [parent.t] + alignment
                parent = parent.p
            return alignment

        for t in petri.semantics.enabled_transitions(sync_net, current_marking):
            new_marking = petri.semantics.execute(t, sync_net, current_marking)
            if new_marking in closed:
                continue
            g = curr.g + cost_function[t]

            if new_marking in marking_map:
                if g >= marking_map[new_marking].g:
                    continue
                h = marking_map[new_marking].h
                open_set.remove(marking_map[new_marking])
            else:
                m_vec = incidence_matrix.encode_marking(new_marking)
                h_obj = sp.linprog(c=cost_vec, A_eq=incidence_matrix.A, b_eq=np.subtract(fin_vec, m_vec))
                h = h_obj['fun']

            tp = SearchTuple(g+h, g, h, new_marking, curr, t)
            heapq.heappush(open_set, tp)
            marking_map[new_marking] = tp


def __vectorize_initial_final_cost(incidence_matrix, ini, fin, cost_function):
    ini_vec = incidence_matrix.encode_marking(ini)
    fini_vec = incidence_matrix.encode_marking(fin)
    cost_vec = [0] * len(cost_function)
    for t in cost_function:
        cost_vec[incidence_matrix.transitions[t]] = cost_function[t]
    return ini_vec, fini_vec, cost_vec


@dataclass(order=True)
class SearchTuple:
    f: float
    g: float = field(compare=False)
    h: float = field(compare=False)
    m: petri.net.Marking = field(compare=False)
    p: Any = field(compare=False)
    t: petri.net.PetriNet.Transition = field(compare=False)




