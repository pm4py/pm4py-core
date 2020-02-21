from collections import Counter

import numpy as np
from numpy.linalg import svd
from scipy.linalg import expm

from pm4py.objects.petri.reachability_graph import construct_reachability_graph
from pm4py.objects.stochastic_petri import tangible_reachability


def get_corr_hex(num):
    """
    Gets correspondence between a number
    and an hexadecimal string

    Parameters
    -------------
    num
        Number

    Returns
    -------------
    hex_string
        Hexadecimal string
    """
    if num < 10:
        return str(int(num))
    elif num < 11:
        return "A"
    elif num < 12:
        return "B"
    elif num < 13:
        return "C"
    elif num < 14:
        return "D"
    elif num < 15:
        return "E"
    elif num < 16:
        return "F"


def get_color_from_probabilities(prob_dictionary):
    """
    Returns colors from a dictionary of probabilities

    Parameters
    -------------
    prob_dictionary
        Dictionary of probabilities

    Returns
    -------------
    color_dictionary
        Dictionary of colors
    """
    color_dictionary = {}

    for state in prob_dictionary:
        value = prob_dictionary[state]
        whiteness = int(255.0 * (1.0 - value))
        w1 = whiteness / 16
        w2 = whiteness % 16
        c1 = get_corr_hex(w1)
        c2 = get_corr_hex(w2)
        color_dictionary[state] = "#FF" + c1 + c2 + c1 + c2

    return color_dictionary


def transient_analysis_from_petri_net_and_smap(net, im, s_map, delay, parameters=None):
    """
    Gets the transient analysis from a Petri net, a stochastic map and a delay

    Parameters
    -------------
    log
        Event log
    delay
        Time delay
    parameters
        Parameters of the algorithm

    Returns
    -------------
    transient_result
        Transient analysis result
    """
    if parameters is None:
        parameters = {}
    # gets the reachability graph from the Petri net
    reachab_graph = construct_reachability_graph(net, im)
    states_reachable_from_start = set()
    for trans in reachab_graph.transitions:
        if str(trans.from_state) == "start1":
            states_reachable_from_start.add(trans.to_state)
    # get the tangible reachability graph from the reachability graph and the stochastic map
    tang_reach_graph = tangible_reachability.get_tangible_reachability_from_reachability(reachab_graph, s_map)
    # gets the Q matrix assuming exponential distributions
    q_matrix = get_q_matrix_from_tangible_exponential(tang_reach_graph, s_map)
    states = sorted(list(tang_reach_graph.states), key=lambda x: x.name)
    states_vector = np.zeros((1, len(states)))

    for state in states_reachable_from_start:
        states_vector[0, states.index(state)] = 1.0 / len(states_reachable_from_start)

    probabilities = transient_analysis_from_tangible_q_matrix_and_states_vector(tang_reach_graph, q_matrix,
                                                                                states_vector, delay)

    color_dictionary = get_color_from_probabilities(probabilities)

    return tang_reach_graph, probabilities, color_dictionary


def get_q_matrix_from_tangible_exponential(tangible_reach_graph, stochastic_info):
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
    q_matrix
        Q-matrix from the tangible reachability graph
    """
    stochastic_info_name = {}
    for s in stochastic_info:
        stochastic_info_name[s.name] = stochastic_info[s]

    states = sorted(list(tangible_reach_graph.states), key=lambda x: x.name)
    no_states = len(states)
    q_matrix = np.zeros((no_states, no_states))

    for i in range(no_states):
        sum_lambda = 0.0
        for trans in states[i].outgoing:
            target_state = trans.to_state
            target_state_index = states.index(target_state)
            if not target_state_index == i:
                sinfo = stochastic_info_name[trans.name]
                lambda_value = 1.0 / float(sinfo.random_variable.scale)
                sum_lambda = sum_lambda + lambda_value
                q_matrix[i, target_state_index] = q_matrix[i, target_state_index] + lambda_value
        q_matrix[i, i] = -sum_lambda

    return q_matrix


def transient_analysis_from_tangible_q_matrix_and_single_state(tangible_reach_graph, q_matrix, source_state, time_diff):
    """
    Do transient analysis from tangible reachability graph, Q matrix and a single state to start from

    Parameters
    -----------
    tangible_reach_graph
        Tangible reachability graph
    q_matrix
        Q matrix
    source_state
        Source state to consider
    time_diff
        Time interval we want to investigate

    Returns
    -----------
    transient_result
        Transient analysis result
    """
    states = sorted(list(tangible_reach_graph.states), key=lambda x: x.name)
    state_index = states.index(source_state)

    states_vector = np.zeros((1, len(states)))
    states_vector[0, state_index] = 1

    return transient_analysis_from_tangible_q_matrix_and_states_vector(tangible_reach_graph, q_matrix, states_vector,
                                                                       time_diff)


def transient_analysis_from_tangible_q_matrix_and_states_vector(tangible_reach_graph, q_matrix, states_vector,
                                                                time_diff):
    """
    Do transient analysis from tangible reachability graph, Q matrix and a vector of probability of states

    Parameters
    ------------
    tangible_reach_graph
        Tangible reachability graph
    q_matrix
        Q matrix
    states_vector
        Vector of states probabilities to start from
    time_diff
        Time interval we want to investigate

    Returns
    -----------
    transient_result
        Transient analysis result
    """
    transient_result = Counter()
    states = sorted(list(tangible_reach_graph.states), key=lambda x: x.name)

    ht_matrix = expm(q_matrix * time_diff)

    res = np.matmul(states_vector, ht_matrix)
    # normalize to 1 the vector of probabilities
    res = res / np.sum(res)

    for i in range(len(states)):
        transient_result[states[i]] = res[0, i]

    return transient_result


def nullspace(a_matrix, atol=1e-13, rtol=0):
    """Compute an approximate basis for the nullspace of A.

    The algorithm used by this function is based on the singular value
    decomposition of `A`.

    Parameters
    ----------
    a_matrix : ndarray
        A should be at most 2-D.  A 1-D array with length k will be treated
        as a 2-D with shape (1, k)
    atol : float
        The absolute tolerance for a zero singular value.  Singular values
        smaller than `atol` are considered to be zero.
    rtol : float
        The relative tolerance.  Singular values less than rtol*smax are
        considered to be zero, where smax is the largest singular value.

    If both `atol` and `rtol` are positive, the combined tolerance is the
    maximum of the two; that is::
        tol = max(atol, rtol * smax)
    Singular values smaller than `tol` are considered to be zero.

    Returns
    ------------
    ns : ndarray
        If `A` is an array with shape (m, k), then `ns` will be an array
        with shape (k, n), where n is the estimated dimension of the
        nullspace of `A`.  The columns of `ns` are a basis for the
        nullspace; each element in numpy.dot(A, ns) will be approximately
        zero.
    """

    a_matrix = np.atleast_2d(a_matrix)
    u, s, vh = svd(a_matrix)
    tol = max(atol, rtol * s[0])
    nnz = (s >= tol).sum()
    ns = vh[nnz:].conj().T
    return ns


def steadystate_analysis_from_tangible_q_matrix(tangible_reach_graph, q_matrix, tol=1e-14):
    """
    Do steadystate analysis from tangible reachability graph and Q matrix

    Parameters
    ------------
    tangible_reach_graph
        Tangible reachability graph
    q_matrix
        Q matrix
    tol
        Tolerance in order to admit states in the steady state

    Returns
    ------------
    steadystate
        Dictionary of states along with their probability in the long term
    """
    q_matrix_trans = np.matrix.transpose(q_matrix)
    if nullspace(q_matrix_trans).shape[1] > 0:
        kernel = np.matrix.transpose(nullspace(q_matrix_trans))[0]
        # normalize to 1 the vector of probabilities
        if np.sum(kernel) < 0:
            kernel = -kernel
        kernel = kernel / np.sum(kernel)
        states = sorted(list(tangible_reach_graph.states), key=lambda x: x.name)
        steadystate = {}
        for i in range(len(states)):
            if kernel[i] > tol:
                steadystate[states[i]] = kernel[i]
        return steadystate
    return None
