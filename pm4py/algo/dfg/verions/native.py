from collections import Counter


def compute_dfg(trace_log, dfg_key='concept:name'):
    dfgs = map((lambda t: [(t[i - 1][dfg_key], t[i][dfg_key]) for i in range(1, len(t))]), trace_log)
    return Counter([dfg for list in dfgs for dfg in list])
