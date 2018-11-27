from pm4py.objects.petri import incidence_matrix
import numpy as np
from scipy.optimize import linprog


def check_source_place_presence(net):
    """
    Check if there is a unique source place with empty connections

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    boolean
        Boolean value that is true when the Petri net has an unique source place with no input connections
    """
    count_empty_input = 0
    for place in net.places:
        if len(place.in_arcs) == 0:
            count_empty_input = count_empty_input + 1
    if count_empty_input == 1:
        return True
    return False


def check_sink_place_presence(net):
    """
    Check if there is a unique sink place with empty connections

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    boolean
        Boolean value that is true when the Petri net has an unique sink place with no output connections
    """
    count_empty_output = 0
    for place in net.places:
        if len(place.out_arcs) == 0:
            count_empty_output = count_empty_output + 1
    if count_empty_output == 1:
        return True
    return False


def check_wfnet(net):
    """
    Check if the Petri net is a workflow net

    Parameters
    ------------
    net
        Petri net

    Returns
    ------------
    boolean
        Boolean value that is true when the Petri net is a workflow net
    """
    source_place_presence = check_source_place_presence(net)
    sink_place_presence = check_sink_place_presence(net)

    return source_place_presence and sink_place_presence


def check_soundness_wfnet(net):
    """
    Check if a workflow net is sound by using the incidence matrix

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    boolean
        Boolean value (True if the WFNet is sound; False if it is not sound)
    """
    matrix = np.asmatrix(incidence_matrix.construct(net).a_matrix)
    matrix = np.transpose(matrix)
    id_matrix = np.identity(matrix.shape[1]) * -1
    vstack_matrix = np.vstack((matrix, id_matrix))
    c = np.ones(matrix.shape[1])
    bub = np.zeros(matrix.shape[0] + matrix.shape[1])
    i = matrix.shape[0]
    while i < matrix.shape[0] + matrix.shape[1]:
        bub[i] = -0.01
        i = i + 1
    try:
        solution = linprog(c, A_ub = vstack_matrix, b_ub = bub)
        if solution.success:
            return True
    except:
        return False
    return False


def check_petri_wfnet_and_soundness(net):
    """
    Check if the provided Petri net is a sound workflow net:
    - firstly, it is checked if it is a workflow net
    - secondly, it is checked if it is a sound workflow net

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    boolean
        Boolean value (True if the Petri net is a sound workflow net)
    """
    is_wfnet = check_wfnet(net)
    #print("is_wfnet = ",is_wfnet)
    if is_wfnet:
        return check_soundness_wfnet(net)
    return False