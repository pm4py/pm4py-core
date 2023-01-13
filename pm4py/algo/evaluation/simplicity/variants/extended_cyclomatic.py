from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils import reachability_graph
from typing import Optional, Dict, Any


def apply(petri_net: PetriNet, im: Optional[Marking] = None, parameters: Optional[Dict[Any, Any]] = None) -> float:
    """
    Computes the extended cyclomatic metric as described in the paper:

    "Complexity Metrics for Workflow Nets"
    Lassen, Kristian Bisgaard, and Wil MP van der Aalst

    Parameters
    -------------
    petri_net
        Petri net

    Returns
    -------------
    ext_cyclomatic_metric
        Extended Cyclomatic metric
    """
    if parameters is None:
        parameters = {}

    import networkx as nx

    if im is None:
        # if not provided, try to reconstruct the initial marking by taking the places with empty preset
        im = Marking()
        for place in petri_net.places:
            if len(place.in_arcs) == 0:
                im[place] = 1

    reach_graph = reachability_graph.construct_reachability_graph(petri_net, im, use_trans_name=True)

    G = nx.DiGraph()
    for n in reach_graph.states:
        G.add_node(n.name)

    for n in reach_graph.states:
        for n2 in n.outgoing:
            G.add_edge(n, n2)

    sg = list(nx.strongly_connected_components(G))

    return len(G.edges) - len(G.nodes) + len(sg)
