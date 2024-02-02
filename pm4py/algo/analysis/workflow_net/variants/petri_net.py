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
import copy

from pm4py.objects.petri_net.utils import petri_utils as pn_utils
from pm4py.objects.petri_net.obj import PetriNet
from typing import Optional, Dict, Any
from pm4py.util import nx_utils


def _short_circuit_petri_net(net):
    """
    Creates a short circuited Petri net,
    whether an unique source place and sink place are there,
    by connecting the sink with the source

    Parameters
    ---------------
    net
        Petri net

    Returns
    ---------------
    boolean
        Boolean value
    """
    s_c_net = copy.deepcopy(net)
    no_source_places = 0
    no_sink_places = 0
    sink = None
    source = None
    for place in s_c_net.places:
        if len(place.in_arcs) == 0:
            source = place
            no_source_places += 1
        if len(place.out_arcs) == 0:
            sink = place
            no_sink_places += 1
    if (sink is not None) and (source is not None) and no_source_places == 1 and no_sink_places == 1:
        # If there is one unique source and sink place, short circuit Petri Net is constructed
        t_1 = PetriNet.Transition("short_circuited_transition", "short_circuited_transition")
        s_c_net.transitions.add(t_1)
        # add arcs in short-circuited net
        pn_utils.add_arc_from_to(sink, t_1, s_c_net)
        pn_utils.add_arc_from_to(t_1, source, s_c_net)
        return s_c_net
    else:
        return None


def apply(net: PetriNet, parameters: Optional[Dict[Any, Any]] = None) -> bool:
    """
    Checks if a Petri net is a workflow net

    Parameters
    ---------------
    net
        Petri net
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    boolean
        Boolean value
    """
    if parameters is None:
        parameters = {}

    scnet = _short_circuit_petri_net(net)
    if scnet is None:
        return False
    nodes = scnet.transitions | scnet.places
    graph = nx_utils.DiGraph()
    while len(nodes) > 0:
        element = nodes.pop()
        graph.add_node(element.name)
        for in_arc in element.in_arcs:
            graph.add_node(in_arc.source.name)
            graph.add_edge(in_arc.source.name, element.name)
        for out_arc in element.out_arcs:
            graph.add_node(out_arc.target.name)
            graph.add_edge(element.name, out_arc.target.name)
    if nx_utils.is_strongly_connected(graph):
        return True
    else:
        return False
