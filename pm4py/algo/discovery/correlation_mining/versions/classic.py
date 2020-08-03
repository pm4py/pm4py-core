from pm4py.util import exec_utils
from enum import Enum
from pm4py.util import constants, xes_constants
from pm4py.objects.conversion.log import converter
from pm4py.objects.log.log import EventStream, Event
from statistics import mean
import numpy as np
from pm4py.util.lp import solver
import pandas as pd


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    INDEX_KEY = "index_key"


DEFAULT_INDEX_KEY = "@@@index"


def apply(stream, parameters=None):
    """
    Apply the correlation miner to an event stream
    (other types of logs are converted to that)

    The approach is described in:
    Pourmirza, Shaya, Remco Dijkman, and Paul Grefen. "Correlation miner: mining business process models and event
    correlations without case identifiers." International Journal of Cooperative Information Systems 26.02 (2017):
    1742002.

    Parameters
    ---------------
    stream
        Event stream
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    dfg
        DFG
    performance_dfg
        Performance DFG (containing the estimated performance for the arcs)
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    index_key = exec_utils.get_param_value(Parameters.INDEX_KEY, parameters, DEFAULT_INDEX_KEY)

    if type(stream) is pd.DataFrame:
        # keep only the two columns before conversion
        stream = stream[[activity_key, timestamp_key]]
    stream = converter.apply(stream, variant=converter.TO_EVENT_STREAM)
    transf_stream = EventStream()
    for idx, ev in enumerate(stream):
        transf_stream.append(
            Event({activity_key: ev[activity_key], timestamp_key: ev[timestamp_key].timestamp(), index_key: idx}))
    transf_stream = sorted(transf_stream, key=lambda x: (x[timestamp_key], x[index_key]))
    activities = sorted(list(set(x[activity_key] for x in transf_stream)))
    activities_grouped = {x: [y for y in transf_stream if y[activity_key] == x] for x in activities}
    PS_matrix = get_precede_succeed_matrix(activities, activities_grouped, timestamp_key)
    duration_matrix = get_duration_matrix(activities, activities_grouped, timestamp_key)
    C_matrix = get_c_matrix(PS_matrix, duration_matrix, activities, activities_grouped)
    dfg, performance_dfg = resolve_LP(C_matrix, duration_matrix, activities, activities_grouped)
    return dfg, performance_dfg


def get_precede_succeed_matrix(activities, activities_grouped, timestamp_key):
    """
    Calculates the precede succeed matrix

    Parameters
    ---------------
    activities
        Ordered list of activities of the log
    activities_grouped
        Grouped list of activities
    timestamp_key
        Timestamp key

    Returns
    ---------------
    precede_succeed_matrix
        Precede succeed matrix
    """
    ret = np.zeros((len(activities), len(activities)))
    for i in range(len(activities)):
        ai = [x[timestamp_key] for x in activities_grouped[activities[i]]]
        for j in range(i + 1, len(activities)):
            aj = [x[timestamp_key] for x in activities_grouped[activities[j]]]
            k = 0
            z = 0
            count = 0
            while k < len(ai):
                while z < len(aj):
                    if ai[k] < aj[z]:
                        break
                    z = z + 1
                count = count + (len(aj) - z)
                k = k + 1
            ret[i, j] = count / float(len(ai) * len(aj))
            ret[j, i] = 1.0 - ret[i, j]

    return ret


def get_duration_matrix(activities, activities_grouped, timestamp_key):
    """
    Calculates the duration matrix

    Parameters
    ---------------
    activities
        Ordered list of activities of the log
    activities_grouped
        Grouped list of activities
    timestamp_key
        Timestamp key

    Returns
    ---------------
    duration_matrix
        Duration matrix
    """
    # greedy algorithm
    ret = np.zeros((len(activities), len(activities)))
    for i in range(len(activities)):
        ai = [x[timestamp_key] for x in activities_grouped[activities[i]]]
        for j in range(len(activities)):
            if not i == j:
                aj = [x[timestamp_key] for x in activities_grouped[activities[j]]]
                k = 0
                z = 0
                times0 = []
                while k < len(ai):
                    while z < len(aj):
                        if ai[k] < aj[z]:
                            times0.append((aj[z] - ai[k]))
                            z = z + 1
                            break
                        z = z + 1
                    k = k + 1
                times0 = mean(times0) if times0 else 0
                k = len(ai) - 1
                z = len(aj) - 1
                times1 = []
                while z >= 0:
                    while k >= 0:
                        if ai[k] < aj[z]:
                            times1.append((aj[z] - ai[k]))
                            k = k - 1
                            break
                        k = k - 1
                    z = z - 1
                times1 = mean(times1) if times1 else 0
                ret[i, j] = min(times0, times1)
    return ret


def get_c_matrix(PS_matrix, duration_matrix, activities, activities_grouped):
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
    activities_grouped
        Grouped dictionary

    Returns
    --------------
    c_matrix
        C matrix
    """
    C_matrix = np.zeros((len(activities), len(activities)))
    for i in range(len(activities)):
        for j in range(len(activities)):
            val = duration_matrix[i, j] / PS_matrix[i, j] * 1 / (
                min(len(activities_grouped[activities[i]]), len(activities_grouped[activities[j]]))) if PS_matrix[
                                                                                                            i, j] > 0 else 0
            if val == 0:
                val = 100000000000
            C_matrix[i, j] = val
    return C_matrix


def resolve_LP(C_matrix, duration_matrix, activities, activities_grouped):
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
    activities_grouped
        Grouped dictionary

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
    activities_occurrences = {i: len(activities_grouped[activities[i]]) for i in range(len(activities))}
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
