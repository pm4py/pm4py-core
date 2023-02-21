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
import numpy as np
from pm4py.util.lp import solver as lp_solver
from pm4py.objects.petri_net.utils import align_utils as utils
from pm4py.objects.petri_net.utils.incidence_matrix import construct
from pm4py.objects.petri_net.utils.petri_utils import decorate_places_preset_trans, decorate_transitions_prepostset
from copy import copy
import heapq


def __search(net, ini, fin):
    cost_function = {t: 1 for t in net.transitions}

    decorate_transitions_prepostset(net)
    decorate_places_preset_trans(net)

    incidence_matrix = construct(net)
    ini_vec, fin_vec, cost_vec = utils.__vectorize_initial_final_cost(incidence_matrix, ini, fin, cost_function)

    closed = set()

    a_matrix = np.asmatrix(incidence_matrix.a_matrix).astype(np.float64)
    g_matrix = -np.eye(len(net.transitions))
    h_cvx = np.matrix(np.zeros(len(net.transitions))).transpose()
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

    h, x = utils.__compute_exact_heuristic_new_version(net, a_matrix, h_cvx, g_matrix, cost_vec, incidence_matrix, ini,
                                                       fin_vec, lp_solver.DEFAULT_LP_SOLVER_VARIANT,
                                                       use_cvxopt=use_cvxopt)
    ini_state = utils.SearchTuple(0 + h, 0, h, ini, None, None, x, True)
    open_set = [ini_state]
    heapq.heapify(open_set)
    visited = 0
    queued = 0
    traversed = 0

    trans_empty_preset = set(t for t in net.transitions if len(t.in_arcs) == 0)

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
            h, x = utils.__compute_exact_heuristic_new_version(net, a_matrix, h_cvx, g_matrix, cost_vec,
                                                               incidence_matrix, curr.m,
                                                               fin_vec, lp_solver.DEFAULT_LP_SOLVER_VARIANT,
                                                               use_cvxopt=use_cvxopt)

            # 11/10/19: shall not a state for which we compute the exact heuristics be
            # by nature a trusted solution?
            tp = utils.SearchTuple(curr.g + h, curr.g, h, curr.m, curr.p, curr.t, x, True)
            # 11/10/2019 (optimization ZA) heappushpop is slightly more efficient than pushing
            # and popping separately
            curr = heapq.heappushpop(open_set, tp)
            current_marking = curr.m

        # max allowed heuristics value (27/10/2019, due to the numerical instability of some of our solvers)
        if curr.h > lp_solver.MAX_ALLOWED_HEURISTICS:
            continue

        # 12/10/2019: do it again, since the marking could be changed
        already_closed = current_marking in closed
        if already_closed:
            continue

        # 12/10/2019: the current marking can be equal to the final marking only if the heuristics
        # (underestimation of the remaining cost) is 0. Low-hanging fruits
        if curr.h < 0.01:
            if current_marking == fin:
                return utils.__reconstruct_alignment(curr, visited, queued, traversed)

        closed.add(current_marking)
        visited += 1

        possible_enabling_transitions = copy(trans_empty_preset)
        for p in current_marking:
            for t in p.ass_trans:
                possible_enabling_transitions.add(t)

        enabled_trans = [t for t in possible_enabling_transitions if t.sub_marking <= current_marking]

        trans_to_visit_with_cost = [(t, cost_function[t]) for t in enabled_trans]

        for t, cost in trans_to_visit_with_cost:
            traversed += 1
            new_marking = utils.add_markings(current_marking, t.add_marking)

            if new_marking in closed:
                continue
            g = curr.g + cost

            queued += 1
            h, x = utils.__derive_heuristic(incidence_matrix, cost_vec, curr.x, t, curr.h)
            trustable = utils.__trust_solution(x)
            new_f = g + h

            tp = utils.SearchTuple(new_f, g, h, new_marking, curr, t, x, trustable)
            heapq.heappush(open_set, tp)
