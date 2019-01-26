import networkx as nx
import numpy as np

from pm4py.objects.petri import incidence_matrix
from pm4py.objects.petri.networkx_graph import create_networkx_undirected_graph
from pm4py.util.lp import factory as lp_solver_factory

DEFAULT_LP_SOLVER_VARIANT = lp_solver_factory.PULP


def check_source_and_sink_reachability(net, unique_source, unique_sink):
    """
    Checks reachability of the source and the sink place from all simulation nodes (places/transitions)
    of the Petri net

    Parameters
    -------------
    net
        Petri net
    unique_source
        Unique source place of the Petri net
    unique_sink
        Unique sink place of the Petri net

    Returns
    -------------
    boolean
        Boolean value that is true if each node is in a path from the source place to the sink place
    """
    graph, unique_source_corr, unique_sink_corr, inv_dictionary = create_networkx_undirected_graph(net, unique_source,
                                                                                                   unique_sink)
    if unique_source_corr is not None and unique_sink_corr is not None:
        nodes_list = list(graph.nodes())
        finish_to_sink = list(nx.ancestors(graph, unique_sink_corr))
        connected_to_source = list(nx.descendants(graph, unique_source_corr))
        if len(finish_to_sink) == len(nodes_list) - 1 and len(connected_to_source) == len(nodes_list) - 1:
            return True
    return False


def check_source_place_presence(net):
    """
    Check if there is a unique source place with empty connections

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    place
        Unique source place (or None otherwise)
    """
    count_empty_input = 0
    unique_source = None
    for place in net.places:
        if len(place.in_arcs) == 0:
            count_empty_input = count_empty_input + 1
            unique_source = place
    if count_empty_input == 1:
        return unique_source
    return None


def check_sink_place_presence(net):
    """
    Check if there is a unique sink place with empty connections

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    place
        Unique source place (or None otherwise)
    """
    count_empty_output = 0
    unique_sink = None
    for place in net.places:
        if len(place.out_arcs) == 0:
            count_empty_output = count_empty_output + 1
            unique_sink = place
    if count_empty_output == 1:
        return unique_sink
    return None


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
    unique_source_place = check_source_place_presence(net)
    unique_sink_place = check_sink_place_presence(net)
    source_sink_reachability = check_source_and_sink_reachability(net, unique_source_place, unique_sink_place)

    return (unique_source_place is not None) and (unique_sink_place is not None) and source_sink_reachability


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
        sol = lp_solver_factory.apply(c, vstack_matrix, bub, None, None, variant=DEFAULT_LP_SOLVER_VARIANT)
        if sol:
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
    # print("is_wfnet = ",is_wfnet)
    if is_wfnet:
        return check_soundness_wfnet(net)
    return False
