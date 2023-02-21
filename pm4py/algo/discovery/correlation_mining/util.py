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
from pm4py.util.lp import solver
from statistics import mean


def get_c_matrix(PS_matrix, duration_matrix, activities, activities_counter):
    """
    Calculates the C-matrix out of the PS matrix and the duration matrix

    Parameters
    --------------
    PS_matrix
        PS matrix
    duration_matrix
        Duration matrix
    activities
        Ordered list of activities of the log
    activities_counter
        Counter of activities

    Returns
    --------------
    c_matrix
        C matrix
    """
    C_matrix = np.zeros((len(activities), len(activities)))
    for i in range(len(activities)):
        for j in range(len(activities)):
            val = duration_matrix[i, j] / PS_matrix[i, j] * 1 / (
                min(activities_counter[activities[i]], activities_counter[activities[j]])) if PS_matrix[
                                                                                                  i, j] > 0 else 0
            if val == 0:
                val = 100000000000
            C_matrix[i, j] = val
    return C_matrix


def resolve_LP(C_matrix, duration_matrix, activities, activities_counter):
    """
    Formulates and solve the LP problem

    Parameters
    --------------
    C_matrix
        C_matrix
    duration_matrix
        Duration matrix
    activities
        Ordered list of activities of the log
    activities_counter
        Counter of activities

    Returns
    -------------
    dfg
        Directly-Follows Graph
    performance_dfg
        Performance DFG (containing the estimated performance for the arcs)
    """
    edges = [(i, j) for i in range(len(activities)) for j in range(len(activities))]
    c = [C_matrix[i, j] for i in range(len(activities)) for j in range(len(activities))]
    edges_sources = {i: [z for z in range(len(edges)) if edges[z][0] == i] for i in range(len(activities))}
    edges_targets = {j: [z for z in range(len(edges)) if edges[z][1] == j] for j in range(len(activities))}
    activities_occurrences = {i: activities_counter[activities[i]] for i in range(len(activities))}
    Aeq = []
    beq = []
    for i in range(len(activities)):
        rec = [0] * len(edges)
        for e in edges_sources[i]:
            rec[e] = 1
        Aeq.append(rec)
        beq.append(activities_occurrences[i])
    for j in range(len(activities)):
        rec = [0] * len(edges)
        for e in edges_targets[j]:
            rec[e] = 1
        Aeq.append(rec)
        beq.append(activities_occurrences[j])
    Aeq = np.asmatrix(Aeq).astype(np.float64)
    beq = np.asmatrix(beq).transpose().astype(np.float64)
    Aub = []
    bub = []
    for i in range(len(activities)):
        for e in edges_sources[i]:
            rec = [0] * len(edges)
            rec[e] = 1
            Aub.append(rec)
            bub.append(activities_occurrences[i])
            rec = [-x for x in rec]
            Aub.append(rec)
            bub.append(0)
    for j in range(len(activities)):
        for e in edges_targets[j]:
            rec = [0] * len(edges)
            rec[e] = 1
            Aub.append(rec)
            bub.append(activities_occurrences[j])
            rec = [-x for x in rec]
            Aub.append(rec)
            bub.append(0)
    Aub = np.asmatrix(Aub).astype(np.float64)
    bub = np.asmatrix(bub).transpose().astype(np.float64)

    use_cvxopt = False
    if solver.DEFAULT_LP_SOLVER_VARIANT == solver.CVXOPT_SOLVER_CUSTOM_ALIGN or solver.DEFAULT_LP_SOLVER_VARIANT == solver.CVXOPT_SOLVER_CUSTOM_ALIGN_ILP:
        use_cvxopt = True

    if use_cvxopt:
        from cvxopt import matrix

        c = matrix(c)
        Aub = matrix(Aub)
        bub = matrix(bub)
        Aeq = matrix(Aeq)
        beq = matrix(beq)

    res = solver.apply(c, Aub, bub, Aeq, beq, variant=solver.DEFAULT_LP_SOLVER_VARIANT)
    points = solver.get_points_from_sol(res, variant=solver.DEFAULT_LP_SOLVER_VARIANT)
    points = [round(p) for p in points]

    dfg = {}
    performance_dfg = {}

    for idx, p in enumerate(points):
        if p > 0:
            dfg[(activities[edges[idx][0]], activities[edges[idx][1]])] = p
            performance_dfg[(activities[edges[idx][0]], activities[edges[idx][1]])] = duration_matrix[
                edges[idx][0], edges[idx][1]]
    return dfg, performance_dfg


def match_return_avg_time(ai, aj, exact=False):
    """
    Matches two list of times (exact or greedy)
    and returns the average.

    Parameters
    --------------
    ai
        First list
    aj
        Second list

    Returns
    ---------------
    times_mean
        Mean of times
    """
    if exact:
        from pm4py.statistics.util import times_bipartite_matching
        matching = times_bipartite_matching.exact_match_minimum_average(ai, aj)
        ret_exact = mean([x[1] - x[0] for x in matching]) if matching else 0
        return ret_exact
    else:
        ret_greedy = greedy_match_return_avg_time(ai, aj)
        return ret_greedy


def greedy_match_return_avg_time(ai, aj):
    """
    Matches two list of times with a greedy method
    and returns the average.

    Parameters
    --------------
    ai
        First list
    aj
        Second list
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    times_mean
        Mean of times
    """
    tm0 = calculate_time_match_fifo(ai, aj)
    td0 = mean([x[1] - x[0] for x in tm0]) if tm0 else 0
    tm1 = calculate_time_match_rlifo(ai, aj)
    td1 = mean([x[1] - x[0] for x in tm1]) if tm1 else 0
    return min(td0, td1)


def calculate_time_match_fifo(ai, aj, times0=None):
    """
    Associate the times between
    two lists of timestamps using FIFO

    Parameters
    --------------
    ai
        First list of timestamps
    aj
        Second list of timestamps
    times0
        Correspondence between execution times

    Returns
    --------------
    times0
        Correspondence between execution times
    """
    if times0 is None:
        times0 = []
    k = 0
    z = 0
    while k < len(ai):
        while z < len(aj):
            if ai[k] < aj[z]:
                times0.append((ai[k], aj[z]))
                z = z + 1
                break
            z = z + 1
        k = k + 1
    return times0


def calculate_time_match_rlifo(ai, aj, times1=None):
    """
    Associate the times between
    two lists of timestamps using LIFO (start from end)

    Parameters
    --------------
    ai
        First list of timestamps
    aj
        Second list of timestamps
    times0
        Correspondence between execution times

    Returns
    --------------
    times0
        Correspondence between execution times
    """
    if times1 is None:
        times1 = []
    k = len(ai) - 1
    z = len(aj) - 1
    while z >= 0:
        while k >= 0:
            if ai[k] < aj[z]:
                times1.append((ai[k], aj[z]))
                k = k - 1
                break
            k = k - 1
        z = z - 1
    return times1
