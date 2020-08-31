import networkx as nx

def create_network_graph(net):
    """
    Transform a given Petri Net in a network graph. Each place and transition is node and gets duplicated.
    The even numbers handle the inputs of a node, the odds the output.
    :param net: PM4Py Petri Net representation
    :return: networkx.DiGraph(), bookkeeping dictionary
    """
    graph = nx.DiGraph()
    places = list(net.places)
    transitions = list(net.transitions)
    nodes=set(places) | set(transitions)
    bookkeeping={}
    for index,el in enumerate(nodes):
        bookkeeping[el]=index*2
    for node in nodes:
        graph.add_node(bookkeeping[node])
        graph.add_node(bookkeeping[node]+1)
        graph.add_edge(bookkeeping[node], bookkeeping[node]+1, capacity=1)
    #add edges for outgoing arcs in former Petri Net
    for element in nodes:
        for arc in element.out_arcs:
            graph.add_edge(bookkeeping[element]+1, bookkeeping[arc.target], capacity=1)
    #add edges for ingoing arcs in former Petri Net
    for element in nodes:
        for arc in element.in_arcs:
            graph.add_edge(bookkeeping[arc.source]+1, bookkeeping[element], capacity=1)
    return graph,bookkeeping

def apply(net):
    """
    Using the max-flow min-cut theorem, we compute a list of nett well handled TP and PT pairs
    (T=transition, P=place)
    :param net: Petri Net
    :return: List
    """
    graph,booking=create_network_graph(net)
    pairs=[]
    for place in net.places:
        for transition in net.transitions:
            p=booking[place]
            t=booking[transition]
            if nx.maximum_flow_value(graph, p+1, t)>1:
                pairs.append((p+1,t))
            if nx.maximum_flow_value(graph, t+1, p)>1:
                pairs.append((t+1,p))
    return pairs
