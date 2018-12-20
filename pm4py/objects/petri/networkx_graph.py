import networkx as nx


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

    graph = nx.Graph()
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


def create_networkx_directed_graph(net):
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
    graph = nx.DiGraph()
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

    return graph, inv_dictionary
