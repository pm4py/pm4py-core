from pm4py.objects import petri

def petri_reduction_treplay(net, parameters=None):
    """
    Apply petri_reduction on the Petrinet removing hidden transitions
    that are unused according to token-based replay

    Parameters
    -----------
    net
        Petri net
    parameters
        Parameters of the algorithm, including:
            aligned_traces -> Result of alignment according to token-based replay
    Returns
    -----------
    net
        Reduced Petri net
    """
    if parameters is None:
        parameters = {}

    aligned_traces = parameters["aligned_traces"]

    enabled_trans_in_at_least_one_trace = set()

    for trace in aligned_traces:
        for trans in trace["activated_transitions"]:
            enabled_trans_in_at_least_one_trace.add(trans)

    transitions = list(net.transitions)
    for trans in transitions:
        if trans.label is None:
            if trans not in enabled_trans_in_at_least_one_trace:
                net = petri.utils.remove_transition(net, trans)

    return net
