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
    timed_transitions = []
    for trans in stochastic_info.keys():
        random_variable = stochastic_info[trans]
        transition_type = random_variable.get_transition_type()
        if transition_type == "TIMED":
            timed_transitions.append(trans.name)
    states_reach = list(reach_graph.states)
    for s in states_reach:
        state_outgoing_trans = list(s.outgoing)
        state_ingoing_trans = list(s.incoming)
        timed_trans_outgoing = [x for x in state_outgoing_trans if x.name in timed_transitions]
        if not len(state_outgoing_trans) == len(timed_trans_outgoing):
            for t in state_outgoing_trans:
                reach_graph.transitions.remove(t)
                t.from_state.outgoing.remove(t)
                t.to_state.incoming.remove(t)
            for t in state_ingoing_trans:
                reach_graph.transitions.remove(t)
                t.from_state.outgoing.remove(t)
                t.to_state.incoming.remove(t)
            reach_graph.states.remove(s)
    states_reach = list(reach_graph.states)
    for s in states_reach:
        if len(s.incoming) == 0 and len(s.outgoing) == 0:
            reach_graph.states.remove(s)

    return reach_graph
