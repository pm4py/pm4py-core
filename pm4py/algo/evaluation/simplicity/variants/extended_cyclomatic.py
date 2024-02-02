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

from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils import reachability_graph
from typing import Optional, Dict, Any
from pm4py.util import nx_utils


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

    if im is None:
        # if not provided, try to reconstruct the initial marking by taking the places with empty preset
        im = Marking()
        for place in petri_net.places:
            if len(place.in_arcs) == 0:
                im[place] = 1

    reach_graph = reachability_graph.construct_reachability_graph(petri_net, im, use_trans_name=True)

    G = nx_utils.DiGraph()
    for n in reach_graph.states:
        G.add_node(n.name)

    for n in reach_graph.states:
        for n2 in n.outgoing:
            G.add_edge(n, n2)

    sg = list(nx_utils.strongly_connected_components(G))

    return len(G.edges) - len(G.nodes) + len(sg)
