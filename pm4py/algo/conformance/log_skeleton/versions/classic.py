from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.algo.discovery.log_skeleton.parameters import CONSIDERED_CONSTRAINTS, DEFAULT_CONSIDERED_CONSTRAINTS
from pm4py.objects.log.util import xes
from pm4py.algo.discovery.log_skeleton import trace_skel


def apply_log(log, model, parameters=None):
    """
    Apply log-skeleton based conformance checking given an event log
    and a log-skeleton model

    Parameters
    --------------
    log
        Event log
    model
        Log-skeleton model
    parameters
        Parameters of the algorithm, including:
        - the activity key (pm4py:param:activity_key)
        - the list of considered constraints (considered_constraints) among: equivalence, always_after, always_before, never_together, directly_follows, activ_freq

    Returns
    --------------
    aligned_traces
        Conformance checking results for each trace:
        - is_fit => boolean that tells if the trace is perfectly fit according to the model
        - dev_fitness => deviation based fitness (between 0 and 1; the more the trace is near to 1 the more fit is)
        - deviations => list of deviations in the model
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    traces = [tuple(y[activity_key] for y in x) for x in log]
    grouped_traces = {}
    gtk = []
    inv_idxs = {}
    for i in range(len(traces)):
        tr = traces[i]
        if not tr in grouped_traces:
            grouped_traces[tr] = []
            gtk.append(tr)
        grouped_traces[tr].append(i)
        inv_idxs[i] = gtk.index(tr)

    res0 = []
    for trace in grouped_traces:
        res0.append(apply_actlist(trace, model, parameters=parameters))

    res = []
    for i in range(len(traces)):
        res.append(res0[inv_idxs[i]])

    return res


def apply_trace(trace, model, parameters=None):
    """
    Apply log-skeleton based conformance checking given a trace
    and a log-skeleton model

    Parameters
    --------------
    trace
        Trace
    model
        Log-skeleton model
    parameters
        Parameters of the algorithm, including:
        - the activity key (pm4py:param:activity_key)
        - the list of considered constraints (considered_constraints) among: equivalence, always_after, always_before, never_together, directly_follows, activ_freq

    Returns
    --------------
    aligned_trace
        Containing:
        - is_fit => boolean that tells if the trace is perfectly fit according to the model
        - dev_fitness => deviation based fitness (between 0 and 1; the more the trace is near to 1 the more fit is)
        - deviations => list of deviations in the model
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    trace = [x[activity_key] for x in trace]

    return apply_actlist(trace, model, parameters=parameters)


def apply_actlist(trace, model, parameters=None):
    """
    Apply log-skeleton based conformance checking given the list of activities of a trace
    and a log-skeleton model

    Parameters
    --------------
    trace
        List of activities of a trace
    model
        Log-skeleton model
    parameters
        Parameters of the algorithm, including:
        - the activity key (pm4py:param:activity_key)
        - the list of considered constraints (considered_constraints) among: equivalence, always_after, always_before, never_together, directly_follows, activ_freq

    Returns
    --------------
    aligned_trace
        Containing:
        - is_fit => boolean that tells if the trace is perfectly fit according to the model
        - dev_fitness => deviation based fitness (between 0 and 1; the more the trace is near to 1 the more fit is)
        - deviations => list of deviations in the model
    """
    if parameters is None:
        parameters = {}

    consid_constraints = parameters[CONSIDERED_CONSTRAINTS] if CONSIDERED_CONSTRAINTS in parameters else DEFAULT_CONSIDERED_CONSTRAINTS
    trace_info = trace_skel.get_trace_info(trace)

    ret = {}
    ret["deviations"] = []
    dev_total = 0
    conf_total = 0

    i = 0
    while i < len(DEFAULT_CONSIDERED_CONSTRAINTS):
        if DEFAULT_CONSIDERED_CONSTRAINTS[i] in consid_constraints:
            if DEFAULT_CONSIDERED_CONSTRAINTS[i] == "activ_freq":
                this_constraints = {x: y for x, y in model[DEFAULT_CONSIDERED_CONSTRAINTS[i]].items()}
                conf_total += len(list(act for act in trace_info[i] if act in this_constraints)) + len(list(act for act in trace_info[i] if act not in this_constraints)) + len(list(act for act in this_constraints if min(this_constraints[act]) > 0 and not act in trace))
                for act in trace_info[i]:
                    if act in this_constraints:
                        if trace_info[i][act] not in this_constraints[act]:
                            dev_total += 1
                            ret["deviations"].append((DEFAULT_CONSIDERED_CONSTRAINTS[i], (act, trace_info[i][act])))
                    else:
                        dev_total += 1
                        ret["deviations"].append((DEFAULT_CONSIDERED_CONSTRAINTS[i], (act, 0)))
                for act in this_constraints:
                    if min(this_constraints[act]) > 0 and not act in trace:
                        dev_total += 1
                        ret["deviations"].append((DEFAULT_CONSIDERED_CONSTRAINTS[i], (act, this_constraints[act])))
            elif DEFAULT_CONSIDERED_CONSTRAINTS[i] == "never_together":
                this_constraints = {x for x in model[DEFAULT_CONSIDERED_CONSTRAINTS[i]] if x[0] in trace}
                conf_total += len(this_constraints)
                setinte = this_constraints.intersection(trace_info[i])
                dev_total += len(setinte)
                if len(setinte) > 0:
                    ret["deviations"].append((DEFAULT_CONSIDERED_CONSTRAINTS[i], tuple(setinte)))
            else:
                this_constraints = {x for x in model[DEFAULT_CONSIDERED_CONSTRAINTS[i]] if x[0] in trace}
                conf_total += len(this_constraints)
                setdiff = this_constraints.difference(trace_info[i])
                dev_total += len(setdiff)
                if len(setdiff) > 0:
                    ret["deviations"].append((DEFAULT_CONSIDERED_CONSTRAINTS[i], tuple(setdiff)))
        i = i + 1
    ret["no_dev_total"] = dev_total
    ret["no_constr_total"] = conf_total
    ret["dev_fitness"] = 1.0 - float(dev_total)/float(conf_total) if conf_total > 0 else 1.0
    ret["deviations"] = sorted(ret["deviations"], key=lambda x: (x[0], x[1]))
    ret["is_fit"] = len(ret["deviations"]) == 0
    return ret
