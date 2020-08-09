from pm4py.algo.discovery.log_skeleton.parameters import Parameters
from pm4py.algo.discovery.log_skeleton.outputs import Outputs as DiscoveryOutputs
from pm4py.objects.log.util import xes
from pm4py.algo.discovery.log_skeleton import trace_skel
from pm4py.algo.conformance.log_skeleton.outputs import Outputs
from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.util import exec_utils, constants


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
        - Parameters.ACTIVITY_KEY
        - Parameters.CONSIDERED_CONSTRAINTS, among: equivalence, always_after, always_before, never_together, directly_follows, activ_freq

    Returns
    --------------
    aligned_traces
        Conformance checking results for each trace:
        - Outputs.IS_FIT => boolean that tells if the trace is perfectly fit according to the model
        - Outputs.DEV_FITNESS => deviation based fitness (between 0 and 1; the more the trace is near to 1 the more fit is)
        - Outputs.DEVIATIONS => list of deviations in the model
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)

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

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)
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

    consid_constraints = exec_utils.get_param_value(Parameters.CONSIDERED_CONSTRAINTS, parameters, Parameters.DEFAULT_CONSIDERED_CONSTRAINTS.value)
    trace_info = trace_skel.get_trace_info(trace)

    ret = {}
    ret[Outputs.DEVIATIONS.value] = []
    dev_total = 0
    conf_total = 0

    default_considered_constraints = Parameters.DEFAULT_CONSIDERED_CONSTRAINTS.value

    i = 0
    while i < len(default_considered_constraints):
        if default_considered_constraints[i] in consid_constraints:
            if default_considered_constraints[i] == DiscoveryOutputs.ACTIV_FREQ.value:
                this_constraints = {x: y for x, y in model[default_considered_constraints[i]].items()}
                conf_total += len(list(act for act in trace_info[i] if act in this_constraints)) + len(list(act for act in trace_info[i] if act not in this_constraints)) + len(list(act for act in this_constraints if min(this_constraints[act]) > 0 and not act in trace))
                for act in trace_info[i]:
                    if act in this_constraints:
                        if trace_info[i][act] not in this_constraints[act]:
                            dev_total += 1
                            ret[Outputs.DEVIATIONS.value].append((default_considered_constraints[i], (act, trace_info[i][act])))
                    else:
                        dev_total += 1
                        ret[Outputs.DEVIATIONS.value].append((default_considered_constraints[i], (act, 0)))
                for act in this_constraints:
                    if min(this_constraints[act]) > 0 and not act in trace:
                        dev_total += 1
                        ret[Outputs.DEVIATIONS.value].append((default_considered_constraints[i], (act, this_constraints[act])))
            elif default_considered_constraints[i] == DiscoveryOutputs.NEVER_TOGETHER.value:
                this_constraints = {x for x in model[default_considered_constraints[i]] if x[0] in trace}
                conf_total += len(this_constraints)
                setinte = this_constraints.intersection(trace_info[i])
                dev_total += len(setinte)
                if len(setinte) > 0:
                    ret[Outputs.DEVIATIONS.value].append((default_considered_constraints[i], tuple(setinte)))
            else:
                this_constraints = {x for x in model[default_considered_constraints[i]] if x[0] in trace}
                conf_total += len(this_constraints)
                setdiff = this_constraints.difference(trace_info[i])
                dev_total += len(setdiff)
                if len(setdiff) > 0:
                    ret[Outputs.DEVIATIONS.value].append((default_considered_constraints[i], tuple(setdiff)))
        i = i + 1
    ret[Outputs.NO_DEV_TOTAL.value] = dev_total
    ret[Outputs.NO_CONSTR_TOTAL.value] = conf_total
    ret[Outputs.DEV_FITNESS.value] = 1.0 - float(dev_total)/float(conf_total) if conf_total > 0 else 1.0
    ret[Outputs.DEVIATIONS.value] = sorted(ret[Outputs.DEVIATIONS.value], key=lambda x: (x[0], x[1]))
    ret[Outputs.IS_FIT.value] = len(ret[Outputs.DEVIATIONS.value]) == 0
    return ret


def apply_from_variants_list(var_list, model, parameters=None):
    """
    Performs conformance checking using the log skeleton,
    applying it from a list of variants

    Parameters
    --------------
    var_list
        List of variants
    model
        Log skeleton model
    parameters
        Parameters

    Returns
    --------------
    conformance_dictio
        Dictionary containing, for each variant, the result
        of log skeleton checking
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)
    variant_delimiter = exec_utils.get_param_value(Parameters.PARAMETER_VARIANT_DELIMITER, parameters,
                                                   constants.DEFAULT_VARIANT_SEP)

    conformance_output = {}

    for cv in var_list:
        v = cv[0]
        tr = v.split(variant_delimiter)
        trace = Trace()
        for act in tr:
            trace.append(Event({activity_key: act}))
        conformance_output[v] = apply_trace(trace, model, parameters=parameters)

    return conformance_output


def after_decode(log_skeleton):
    """
    Prepares the log skeleton after decoding

    Parameters
    --------------
    log_skeleton
        Log skeleton

    Returns
    --------------
    log_skeleton
        Log skeleton (with sets instead of lists)
    """
    log_skeleton[DiscoveryOutputs.EQUIVALENCE.value] = set(log_skeleton[DiscoveryOutputs.EQUIVALENCE.value])
    log_skeleton[DiscoveryOutputs.ALWAYS_AFTER.value] = set(log_skeleton[DiscoveryOutputs.ALWAYS_AFTER.value])
    log_skeleton[DiscoveryOutputs.ALWAYS_BEFORE.value] = set(log_skeleton[DiscoveryOutputs.ALWAYS_BEFORE.value])
    log_skeleton[DiscoveryOutputs.NEVER_TOGETHER.value] = set(log_skeleton[DiscoveryOutputs.NEVER_TOGETHER.value])
    log_skeleton[DiscoveryOutputs.DIRECTLY_FOLLOWS.value] = set(log_skeleton[DiscoveryOutputs.DIRECTLY_FOLLOWS.value])
    for act in log_skeleton[DiscoveryOutputs.ACTIV_FREQ.value]:
        log_skeleton[DiscoveryOutputs.ACTIV_FREQ.value][act] = set(log_skeleton[DiscoveryOutputs.ACTIV_FREQ.value][act])
    return log_skeleton
