import numpy as np
from pm4py.util.lp import factory as lp_solver_factory
from pm4py.objects.petri.petrinet import Marking
from pm4py.objects.petri import semantics
from copy import copy
import sys


SKIP = '>>'
STD_MODEL_LOG_MOVE_COST = 10000
STD_TAU_COST = 1
STD_SYNC_COST = 0


def construct_standard_cost_function(synchronous_product_net, skip):
    """
    Returns the standard cost function, which is:
    * event moves: cost 1000
    * model moves: cost 1000
    * tau moves: cost 1
    * sync moves: cost 0
    :param synchronous_product_net:
    :param skip:
    :return:
    """
    costs = {}
    for t in synchronous_product_net.transitions:
        if (skip == t.label[0] or skip == t.label[1]) and (t.label[0] is not None and t.label[1] is not None):
            costs[t] = STD_MODEL_LOG_MOVE_COST
        else:
            if skip == t.label[0] and t.label[1] is None:
                costs[t] = STD_TAU_COST
            else:
                costs[t] = STD_SYNC_COST
    return costs


def pretty_print_alignments(alignments):
    """
    Takes an alignment and prints it to the console, e.g.:
     A  | B  | C  | D  |
    --------------------
     A  | B  | C  | >> |
    :param alignment: <class 'list'>
    :return: Nothing
    """
    if isinstance(alignments, list):
        for alignment in alignments:
            __print_single_alignment(alignment["alignment"])
    else:
        __print_single_alignment(alignments["alignment"])


def __print_single_alignment(step_list):
    trace_steps = []
    model_steps = []
    max_label_length = 0
    for step in step_list:
        trace_steps.append(" " + str(step[0]) + " ")
        model_steps.append(" " + str(step[1]) + " ")
        if len(step[0]) > max_label_length:
            max_label_length = len(str(step[0]))
        if len(str(step[1])) > max_label_length:
            max_label_length = len(str(step[1]))
    for i in range(len(trace_steps)):
        if len(str(trace_steps[i])) - 2 < max_label_length:
            step_length = len(str(trace_steps[i])) - 2
            spaces_to_add = max_label_length - step_length
            for j in range(spaces_to_add):
                if j % 2 == 0:
                    trace_steps[i] = trace_steps[i] + " "
                else:
                    trace_steps[i] = " " + trace_steps[i]
        print(trace_steps[i], end='|')
    divider = ""
    length_divider = len(trace_steps) * (max_label_length + 3)
    for i in range(length_divider):
        divider += "-"
    print('\n' + divider)
    for i in range(len(model_steps)):
        if len(model_steps[i]) - 2 < max_label_length:
            step_length = len(model_steps[i]) - 2
            spaces_to_add = max_label_length - step_length
            for j in range(spaces_to_add):
                if j % 2 == 0:
                    model_steps[i] = model_steps[i] + " "
                else:
                    model_steps[i] = " " + model_steps[i]

        print(model_steps[i], end='|')
    print('\n\n')


def add_markings(curr, add):
    m = Marking()
    for p in curr.items():
        m[p[0]] = p[1]
    for p in add.items():
        m[p[0]] += p[1]
        if m[p[0]] == 0:
            del m[p[0]]
    return m


def __get_alt(open_set, new_marking):
    for item in open_set:
        if item.m == new_marking:
            return item


def __reconstruct_alignment(state, visited, queued, traversed, ret_tuple_as_trans_desc=False):
    parent = state.p
    if ret_tuple_as_trans_desc:
        alignment = [(state.t.name, state.t.label)]
        while parent.p is not None:
            alignment = [(parent.t.name, parent.t.label)] + alignment
            parent = parent.p
    else:
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


def __compute_exact_heuristic_new_version(sync_net, a_matrix, h_cvx, g_matrix, cost_vec, incidence_matrix,
                                          marking, fin_vec, variant, use_cvxopt=False):
    m_vec = incidence_matrix.encode_marking(marking)
    b_term = [i - j for i, j in zip(fin_vec, m_vec)]
    b_term = np.matrix([x * 1.0 for x in b_term]).transpose()

    if use_cvxopt:
        # not available in the latest version of PM4Py
        from cvxopt import matrix

        b_term = matrix(b_term)

    parameters_solving = {"solver": "glpk"}

    sol = lp_solver_factory.apply(cost_vec, g_matrix, h_cvx, a_matrix, b_term, parameters=parameters_solving,
                                  variant=variant)
    prim_obj = lp_solver_factory.get_prim_obj_from_sol(sol, variant=variant)
    points = lp_solver_factory.get_points_from_sol(sol, variant=variant)

    prim_obj = prim_obj if prim_obj is not None else sys.maxsize
    points = points if points is not None else [0.0] * len(sync_net.transitions)

    return prim_obj, points


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


class SearchTuple:
    def __init__(self, f, g, h, m, p, t, x, trust):
        self.f = f
        self.g = g
        self.h = h
        self.m = m
        self.p = p
        self.t = t
        self.x = x
        self.trust = trust

    def __lt__(self, other):
        if self.f < other.f:
            return True
        elif other.f < self.f:
            return False
        elif self.trust and not other.trust:
            return True
        else:
            return self.h < other.h

    def __get_firing_sequence(self):
        ret = []
        if self.p is not None:
            ret = ret + self.p.__get_firing_sequence()
        if self.t is not None:
            ret.append(self.t)
        return ret

    def __repr__(self):
        string_build = ["\nm=" + str(self.m), " f=" + str(self.f), ' g=' + str(self.g), " h=" + str(self.h),
                        " path=" + str(self.__get_firing_sequence()) + "\n\n"]
        return " ".join(string_build)


class DijkstraSearchTuple:
    def __init__(self, g, m, p, t, l):
        self.g = g
        self.m = m
        self.p = p
        self.t = t
        self.l = l

    def __lt__(self, other):
        if self.g < other.g:
            return True
        elif other.g < self.g:
            return False
        else:
            return other.l < self.l

    def __get_firing_sequence(self):
        ret = []
        if self.p is not None:
            ret = ret + self.p.__get_firing_sequence()
        if self.t is not None:
            ret.append(self.t)
        return ret

    def __repr__(self):
        string_build = ["\nm=" + str(self.m), " g=" + str(self.g),
                        " path=" + str(self.__get_firing_sequence()) + "\n\n"]
        return " ".join(string_build)


def get_visible_transitions_eventually_enabled_by_marking(net, marking):
    """
    Get visible transitions eventually enabled by marking (passing possibly through hidden transitions)
    Parameters
    ----------
    net
        Petri net
    marking
        Current marking
    """
    all_enabled_transitions = list(semantics.enabled_transitions(net, marking))
    initial_all_enabled_transitions_marking_dictio = {}
    all_enabled_transitions_marking_dictio = {}
    for trans in all_enabled_transitions:
        all_enabled_transitions_marking_dictio[trans] = marking
        initial_all_enabled_transitions_marking_dictio[trans] = marking
    visible_transitions = set()
    visited_transitions = set()

    i = 0
    while i < len(all_enabled_transitions):
        t = all_enabled_transitions[i]
        marking_copy = copy(all_enabled_transitions_marking_dictio[t])

        if repr([t, marking_copy]) not in visited_transitions:
            if t.label is not None:
                visible_transitions.add(t)
            else:
                if semantics.is_enabled(t, net, marking_copy):
                    new_marking = semantics.execute(t, net, marking_copy)
                    new_enabled_transitions = list(semantics.enabled_transitions(net, new_marking))
                    for t2 in new_enabled_transitions:
                        all_enabled_transitions.append(t2)
                        all_enabled_transitions_marking_dictio[t2] = new_marking
            visited_transitions.add(repr([t, marking_copy]))
        i = i + 1

    return visible_transitions
