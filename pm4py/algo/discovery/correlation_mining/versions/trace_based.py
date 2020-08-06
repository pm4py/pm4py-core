from pm4py.util import exec_utils
from enum import Enum
from pm4py.util import constants, xes_constants
from pm4py.objects.conversion.log import converter
from pm4py.algo.discovery.correlation_mining import util as cm_util
from statistics import mean
import numpy as np
from collections import Counter


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    INDEX_KEY = "index_key"


DEFAULT_INDEX_KEY = "@@@index"


def apply(log, parameters=None):
    if parameters is None:
        parameters = {}
    log = converter.apply(log, parameters=parameters)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    index_key = exec_utils.get_param_value(Parameters.INDEX_KEY, parameters, DEFAULT_INDEX_KEY)

    traces_list = []
    for trace in log:
        trace_stream = [
            {activity_key: trace[i][activity_key], timestamp_key: trace[i][timestamp_key].timestamp(), index_key: i} for
            i in range(len(trace))]
        trace_stream = sorted(trace_stream, key=lambda x: (x[timestamp_key], x[index_key]))
        traces_list.append(trace_stream)

    activities_counter = Counter([y[activity_key] for x in traces_list for y in x])
    activities = sorted(list(activities_counter))
    trace_grouped_list = []
    for trace in traces_list:
        gr = []
        for act in activities:
            act_gr = [x for x in trace if x[activity_key] == act]
            gr.append(act_gr)
        trace_grouped_list.append(gr)

    PS_matrix = get_precede_succeed_matrix(activities, trace_grouped_list, timestamp_key)
    duration_matrix = get_duration_matrix(activities, trace_grouped_list, timestamp_key)
    C_matrix = cm_util.get_c_matrix(PS_matrix, duration_matrix, activities, activities_counter)
    dfg, performance_dfg = cm_util.resolve_LP(C_matrix, duration_matrix, activities, activities_counter)
    return dfg, performance_dfg


def get_precede_succeed_matrix(activities, trace_grouped_list, timestamp_key):
    ret = np.zeros((len(activities), len(activities)))
    for i in range(len(activities)):
        for j in range(i + 1, len(activities)):
            count = 0
            total = 0
            for tr in trace_grouped_list:
                ai = [x[timestamp_key] for x in tr[i]]
                aj = [x[timestamp_key] for x in tr[j]]
                if ai and aj:
                    total += len(ai) * len(aj)
                    k = 0
                    z = 0
                    while k < len(ai):
                        while z < len(aj):
                            if ai[k] < aj[z]:
                                break
                            z = z + 1
                        count = count + (len(aj) - z)
                        k = k + 1
            if total > 0:
                ret[i, j] = count / float(total)
            ret[j, i] = 1.0 - ret[i, j]
    return ret


def get_duration_matrix(activities, trace_grouped_list, timestamp_key):
    ret = np.zeros((len(activities), len(activities)))
    for i in range(len(activities)):
        for j in range(len(activities)):
            if not i == j:
                times0 = []
                times1 = []
                for tr in trace_grouped_list:
                    ai = [x[timestamp_key] for x in tr[i]]
                    aj = [x[timestamp_key] for x in tr[j]]
                    if ai and aj:
                        # FIFO
                        k = 0
                        z = 0
                        while k < len(ai):
                            while z < len(aj):
                                if ai[k] < aj[z]:
                                    times0.append((aj[z] - ai[k]))
                                    z = z + 1
                                    break
                                z = z + 1
                            k = k + 1
                        # LIFO
                        k = len(ai) - 1
                        z = len(aj) - 1
                        while z >= 0:
                            while k >= 0:
                                if ai[k] < aj[z]:
                                    times1.append((aj[z] - ai[k]))
                                    k = k - 1
                                    break
                                k = k - 1
                            z = z - 1
                times0 = mean(times0) if times0 else 0
                times1 = mean(times1) if times1 else 0
                ret[i, j] = min(times0, times1)
    return ret
