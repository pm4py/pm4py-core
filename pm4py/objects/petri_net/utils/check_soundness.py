'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from pm4py.objects.petri_net.utils.networkx_graph import create_networkx_undirected_graph
from pm4py.objects.petri_net.utils import explore_path
from pm4py.objects.petri_net import obj
from pm4py.util import nx_utils


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
        finish_to_sink = list(nx_utils.ancestors(graph, unique_sink_corr))
        connected_to_source = list(nx_utils.descendants(graph, unique_source_corr))
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


def check_source_sink_place_conditions(net):
    """
    Check some conditions on the source/sink place important
    for a sound workflow net

    Parameters
    --------------
    net
        Petri net

    Returns
    --------------
    boolean
        Boolean value (True is good)
    """
    # check also that the transitions connected to the source/sink place have unique arcs
    unique_source_place = check_source_place_presence(net)
    unique_sink_place = check_sink_place_presence(net)
    if unique_source_place is not None:
        for arc in unique_source_place.out_arcs:
            trans = arc.target
            if len(trans.in_arcs) > 1:
                return False
    if unique_sink_place is not None:
        for arc in unique_sink_place.in_arcs:
            trans = arc.source
            if len(trans.out_arcs) > 1:
                return False
    return True


def check_easy_soundness_net_in_fin_marking(net, ini, fin):
    """
    Checks the easy soundness of a Petri net having the initial and the final marking

    Parameters
    -------------
    net
        Petri net
    ini
        Initial marking
    fin
        Final marking

    Returns
    -------------
    boolean
        Boolean value
    """
    try:
        alignment = explore_path.__search(net, ini, fin)
        if alignment is not None:
            return True
        return False
    except:
        return False


def check_easy_soundness_of_wfnet(net):
    """
    Checks the easy soundness of a workflow net

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    boolean
        Boolean value
    """
    source = list(x for x in net.places if len(x.in_arcs) == 0)[0]
    sink = list(x for x in net.places if len(x.out_arcs) == 0)[0]

    ini = obj.Marking({source: 1})
    fin = obj.Marking({sink: 1})

    return check_easy_soundness_net_in_fin_marking(net, ini, fin)
