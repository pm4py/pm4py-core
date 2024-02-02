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
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.util import nx_utils


def create_networkx_undirected_graph(net, unique_source, unique_sink):
    """
    Create a NetworkX undirected graph from a Petri net, returning also correspondences for the unique
    source and the unique sink places that were discovered

    Parameters
    -------------
    net
        Petri net
    unique_source
        Unique source place
    unique_sink
        Unique sink place

    Returns
    -------------
    graph
        NetworkX graph
    unique_source_corr
        Correspondence in the NetworkX graph of the unique source place
    unique_sink_corr
        Correspondence in the NetworkX graph of the unique sink place
    inv_dictionary
        Correspondence between NetworkX nodes and Petri net entities
    """
    graph = nx_utils.Graph()
    dictionary = {}
    inv_dictionary = {}
    for place in net.places:
        value = len(dictionary)
        dictionary[place] = value
        inv_dictionary[value] = place
        graph.add_node(dictionary[place])
    for transition in net.transitions:
        value = len(dictionary)
        dictionary[transition] = value
        inv_dictionary[value] = transition
        graph.add_node(dictionary[transition])
    for arc in net.arcs:
        graph.add_edge(dictionary[arc.source], dictionary[arc.target])
    unique_source_corr = dictionary[unique_source] if unique_source in dictionary else None
    unique_sink_corr = dictionary[unique_sink] if unique_sink in dictionary else None

    return graph, unique_source_corr, unique_sink_corr, inv_dictionary


def create_networkx_directed_graph(net, weight=None):
    """
    Create a NetworkX directed graph from a Petri net

    Parameters
    --------------
    net
        Petri net

    Returns
    --------------
    graph
        NetworkX digraph
    inv_dictionary
        Correspondence between NetworkX nodes and Petri net entities
    """
    # forward to new function
    G, d, id = create_networkx_directed_graph_ret_dict_both_ways(net,weight)
    return G,id

def create_networkx_directed_graph_ret_dict_both_ways(net, weight=None):
    """
    Create a NetworkX directed graph from a Petri net

    Parameters
    --------------
    net
        Petri net

    Returns
    --------------
    graph
        NetworkX digraph
    dictionary
        dict mapping Petri net nodes to NetworkX nodes
    inv_dictionary
        dict mapping NetworkX nodes to Petri net nodes
    """
    graph = nx_utils.DiGraph()
    dictionary = {}
    inv_dictionary = {}
    for place in net.places:
        value = len(dictionary)
        dictionary[place] = value
        inv_dictionary[value] = place
        graph.add_node(dictionary[place])
    for transition in net.transitions:
        value = len(dictionary)
        dictionary[transition] = value
        inv_dictionary[value] = transition
        graph.add_node(dictionary[transition])
    for arc in net.arcs:
        source = dictionary[arc.source]
        target = dictionary[arc.target]
        graph.add_edge(source, target)
        if weight is not None:
            if type(inv_dictionary[source]) is PetriNet.Transition:
                graph.edges[source, target]["weight"] = weight[inv_dictionary[source]]
            else:
                graph.edges[source, target]["weight"] = weight[inv_dictionary[target]]
    return graph, dictionary, inv_dictionary
