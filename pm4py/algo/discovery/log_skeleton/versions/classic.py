from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.algo.discovery.log_skeleton.parameters import NOISE_THRESHOLD
from pm4py.objects.log.util import xes
from collections import Counter
from pm4py.algo.discovery.log_skeleton import trace_skel
import math


def equivalence(logs_traces, all_activs, noise_threshold=0):
    """
    Gets the equivalence relations given the traces of the log

    Parameters
    -------------
    logs_traces
        Traces of the log
    all_activs
        All the activities
    noise_threshold
        Noise threshold

    Returns
    --------------
    rel
        List of relations in the log
    """
    ret0 = Counter()
    for trace in logs_traces:
        rs = Counter(trace_skel.equivalence(list(trace)))
        for k in rs:
            rs[k] = rs[k] * logs_traces[trace]
        ret0 += rs
    ret = set(x for x, y in ret0.items() if y >= all_activs[x[0]] * (1.0 - noise_threshold))
    return ret


def always_after(logs_traces, all_activs, noise_threshold=0):
    """
    Gets the always-after relations given the traces of the log

    Parameters
    -------------
    logs_traces
        Traces of the log
    all_activs
        All the activities
    noise_threshold
        Noise threshold

    Returns
    --------------
    rel
        List of relations in the log
    """
    ret0 = Counter()
    for trace in logs_traces:
        rs = Counter(trace_skel.after(list(trace)))
        for k in rs:
            rs[k] = rs[k] * logs_traces[trace]
        ret0 += rs
    ret = set(x for x,y in ret0.items() if y >= all_activs[x[0]] * (1.0 - noise_threshold))
    return ret


def always_before(logs_traces, all_activs, noise_threshold=0):
    """
    Gets the always-before relations given the traces of the log

    Parameters
    -------------
    logs_traces
        Traces of the log
    all_activs
        All the activities
    noise_threshold
        Noise threshold

    Returns
    --------------
    rel
        List of relations in the log
    """
    ret0 = Counter()
    for trace in logs_traces:
        rs = Counter(trace_skel.before(list(trace)))
        for k in rs:
            rs[k] = rs[k] * logs_traces[trace]
        ret0 += rs
    ret = set(x for x,y in ret0.items() if y >= all_activs[x[0]] * (1.0 - noise_threshold))
    return ret


def never_together(logs_traces, all_activs, len_log, noise_threshold=0):
    """
    Gets the never-together relations given the traces of the log

    Parameters
    -------------
    logs_traces
        Traces of the log
    all_activs
        All the activities
    len_log
        Length of the log
    noise_threshold
        Noise threshold

    Returns
    --------------
    rel
        List of relations in the log
    """
    all_combos = set((x, y) for x in all_activs for y in all_activs if x != y)
    ret0 = Counter()
    for k in all_combos:
        ret0[k] = all_activs[k[0]]
    for trace in logs_traces:
        rs = Counter(trace_skel.combos(list(trace)))
        for k in rs:
            rs[k] = rs[k] * logs_traces[trace]
        ret0 -= rs
    ret = set(x for x, y in ret0.items() if y >= all_activs[x[0]] * (1.0 - noise_threshold))
    return ret


def directly_follows(logs_traces, all_activs, noise_threshold=0):
    """
    Gets the allowed directly-follows relations given the traces of the log

    Parameters
    -------------
    logs_traces
        Traces of the log
    all_activs
        All the activities
    noise_threshold
        Noise threshold

    Returns
    --------------
    rel
        List of relations in the log
    """
    ret0 = Counter()
    for trace in logs_traces:
        rs = Counter(trace_skel.directly_follows(list(trace)))
        for k in rs:
            rs[k] = rs[k] * logs_traces[trace]
        ret0 += rs
    ret = set(x for x,y in ret0.items() if y >= all_activs[x[0]] * (1.0 - noise_threshold))
    return ret


def activ_freq(logs_traces, all_activs, len_log, noise_threshold=0):
    """
    Gets the allowed activities frequencies given the traces of the log

    Parameters
    -------------
    logs_traces
        Traces of the log
    all_activs
        All the activities
    len_log
        Length of the log
    noise_threshold
        Noise threshold

    Returns
    --------------
    rel
        List of relations in the log
    """
    ret0 = {}
    ret = {}
    for trace in logs_traces:
        rs = trace_skel.activ_freq(trace)
        for act in all_activs:
            if act not in rs:
                rs[act] = 0
        for act in rs:
            if act not in ret0:
                ret0[act] = Counter()
            ret0[act][rs[act]] += logs_traces[trace]
    for act in ret0:
        ret0[act] = sorted(list((x,y) for x,y in ret0[act].items()), key=lambda x: x[1], reverse=True)
        added = 0
        i = 0
        while i < len(ret0[act]):
            added += ret0[act][i][1]
            if added >= (1.0 - noise_threshold) * len_log:
                ret0[act] = ret0[act][:min(i+1, len(ret0[act]))]
            i = i + 1
        ret[act] = set(x[0] for x in ret0[act])
    return ret


def apply(log, parameters=None):
    """
    Discover a log skeleton from an event log

    Parameters
    -------------
    log
        Event log
    parameters
        Parameters of the algorithm, including:
            - the activity key (pm4py:param:activity_key)
            - the noise threshold (noise_threshold)

    Returns
    -------------
    model
        Log skeleton model
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    noise_threshold = parameters[NOISE_THRESHOLD] if NOISE_THRESHOLD in parameters else 0.0

    logs_traces = Counter([tuple(y[activity_key] for y in x) for x in log])
    all_activs = Counter(list(y[activity_key] for x in log for y in x))

    ret = {}
    ret["equivalence"] = equivalence(logs_traces, all_activs, noise_threshold=noise_threshold)
    ret["always_after"] = always_after(logs_traces, all_activs, noise_threshold=noise_threshold)
    ret["always_before"] = always_before(logs_traces, all_activs, noise_threshold=noise_threshold)
    ret["never_together"] = never_together(logs_traces, all_activs, len(log), noise_threshold=noise_threshold)
    ret["directly_follows"] = directly_follows(logs_traces, all_activs, noise_threshold=noise_threshold)
    ret["activ_freq"] = activ_freq(logs_traces, all_activs, len(log), noise_threshold=noise_threshold)

    return ret
