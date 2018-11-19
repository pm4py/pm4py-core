def get_tangible_reachability_from_reachability(reach_graph, stochastic_info):
    """
    Gets the tangible reachability graph from the reachability graph and the stochastic transition map

    Parameters
    ------------
    reach_graph
        Reachability graph
    stochastic_info
        Stochastic information

    Returns
    ------------
    tangible_reach_graph
        Tangible reachability graph
    """
    timed_or_hidden_transitions = []
    for trans in stochastic_info.keys():
        random_variable = stochastic_info[trans]
        transition_type = random_variable.get_transition_type()
        if transition_type == "TIMED" or trans.label is None:
            timed_or_hidden_transitions.append(trans.name)
    transitions_reach = list(reach_graph.transitions)
    for t in transitions_reach:
        if t.name not in timed_or_hidden_transitions:
            reach_graph.transitions.remove(t)
            t.from_state.outgoing.remove(t)
            t.to_state.incoming.remove(t)
    states_reach = list(reach_graph.states)
    for s in states_reach:
        if len(s.incoming) == 0 and len(s.outgoing) == 0:
            reach_graph.states.remove(s)

    return reach_graph