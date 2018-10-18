from pm4py.objects import petri


def clean_duplicate_transitions(net):
    """
    Clean duplicate transitions in a Petri net

    Parameters
    ------------
    net
        Petri net

    Returns
    ------------
    net
        Cleaned Petri net
    """
    transitions = list(net.transitions)
    already_visited_combo = set()
    for i in range(0, len(transitions)):
        trans = transitions[i]
        if trans.label is None:
            in_arcs = trans.in_arcs
            out_arcs = trans.out_arcs
            to_delete = False
            for in_arc in in_arcs:
                in_place = in_arc.source
                for out_arc in out_arcs:
                    out_place = out_arc.target
                    combo = in_place.name + " " + out_place.name
                    if combo in already_visited_combo:
                        to_delete = True
                        break
                    already_visited_combo.add(combo)
            if to_delete:
                net = petri.utils.remove_transition(net, trans)
    return net


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
