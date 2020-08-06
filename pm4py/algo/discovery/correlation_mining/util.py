import numpy as np
from pm4py.util.lp import solver

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

    res = solver.apply(c, Aub, bub, Aeq, beq)
    points = solver.get_points_from_sol(res)
    points = [round(p) for p in points]

    dfg = {}
    performance_dfg = {}

    for idx, p in enumerate(points):
        if p > 0:
            dfg[(activities[edges[idx][0]], activities[edges[idx][1]])] = p
            performance_dfg[(activities[edges[idx][0]], activities[edges[idx][1]])] = duration_matrix[
                edges[idx][0], edges[idx][1]]
    return dfg, performance_dfg
