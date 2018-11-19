import numpy as np

def get_Q_matrix_from_tangible_exponential(tangible_reach_graph, stochastic_info):
    """
    Gets Q matrix from tangible reachability graph and stochastic map where the
    distribution type has been forced to be exponential

    Parameters
    -----------
    tangible_reach_graph
        Tangible reachability graph
    stochastic_info
        Stochastic map for each transition

    Returns
    -----------
    Q_matrix
        Q-matrix from the tangible reachability graph
    """
    stochastic_info_name = {}
    for s in stochastic_info:
        stochastic_info_name[s.name] = stochastic_info[s]

    states = sorted(list(tangible_reach_graph.states), key=lambda x: x.name)
    no_states = len(states)
    Q_matrix = np.zeros((no_states, no_states))

    for i in range(no_states):
        sum_lambda = 0.0
        for trans in states[i].outgoing:
            target_state = trans.to_state
            target_state_index = states.index(target_state)
            if not target_state_index == i:
                sinfo = stochastic_info_name[trans.name]
                lambda_value = 1.0 / float(sinfo.random_variable.scale)
                sum_lambda = sum_lambda + lambda_value
                Q_matrix[i, target_state_index] = lambda_value
        Q_matrix[i, i] = -sum_lambda

    return Q_matrix