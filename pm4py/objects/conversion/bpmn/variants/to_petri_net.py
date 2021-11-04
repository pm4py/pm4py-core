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
import uuid
from enum import Enum

from pm4py.objects.petri_net.utils import reduction
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to
from pm4py.util import exec_utils


class Parameters(Enum):
    USE_ID = "use_id"


def build_digraph_from_petri_net(net):
    """
    Builds a directed graph from a Petri net
        (for the purpose to add invisibles between inclusive gateways)

    Parameters
    -------------
    net
        Petri net

    Returns
    -------------
    digraph
        Digraph
    """
    import networkx as nx
    graph = nx.DiGraph()
    for place in net.places:
        graph.add_node(place.name)
    for trans in net.transitions:
        in_places = [x.source for x in list(trans.in_arcs)]
        out_places = [x.target for x in list(trans.out_arcs)]
        for pl1 in in_places:
            for pl2 in out_places:
                graph.add_edge(pl1.name, pl2.name)
    return graph


def apply(bpmn_graph, parameters=None):
    """
    Converts a BPMN graph to an accepting Petri net

    Parameters
    --------------
    bpmn_graph
        BPMN graph
    parameters
        Parameters of the algorithm

    Returns
    --------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    if parameters is None:
        parameters = {}

    import networkx as nx
    from pm4py.objects.bpmn.obj import BPMN

    use_id = exec_utils.get_param_value(Parameters.USE_ID, parameters, False)

    net = PetriNet("")
    source_place = PetriNet.Place("source")
    net.places.add(source_place)
    sink_place = PetriNet.Place("sink")
    net.places.add(sink_place)
    im = Marking()
    fm = Marking()
    im[source_place] = 1
    fm[sink_place] = 1

    # keep this correspondence for adding invisible transitions for OR-gateways
    inclusive_gateway_exit = set()
    inclusive_gateway_entry = set()

    flow_place = {}
    source_count = {}
    target_count = {}
    for flow in bpmn_graph.get_flows():
        source = flow.get_source()
        target = flow.get_target()
        place = PetriNet.Place(str(flow.get_id()))
        net.places.add(place)
        flow_place[flow] = place
        if source not in source_count:
            source_count[source] = 0
        if target not in target_count:
            target_count[target] = 0
        source_count[source] = source_count[source] + 1
        target_count[target] = target_count[target] + 1

    for flow in bpmn_graph.get_flows():
        source = flow.get_source()
        target = flow.get_target()
        place = PetriNet.Place(str(flow.get_id()))
        if isinstance(source, BPMN.InclusiveGateway) and source_count[source] > 1:
            inclusive_gateway_exit.add(place.name)
        elif isinstance(target, BPMN.InclusiveGateway) and target_count[target] > 1:
            inclusive_gateway_entry.add(place.name)

    # remove possible places that are both in inclusive_gateway_exit and inclusive_gateway_entry,
    # because we do not need to add invisibles in this situation
    incl_gat_set_inters = inclusive_gateway_entry.intersection(inclusive_gateway_exit)
    inclusive_gateway_exit = inclusive_gateway_exit.difference(incl_gat_set_inters)
    inclusive_gateway_entry = inclusive_gateway_entry.difference(incl_gat_set_inters)

    nodes_entering = {}
    nodes_exiting = {}
    for node in bpmn_graph.get_nodes():
        entry_place = PetriNet.Place("ent_" + str(node.get_id()))
        net.places.add(entry_place)
        exiting_place = PetriNet.Place("exi_" + str(node.get_id()))
        net.places.add(exiting_place)
        if use_id:
            label = str(node.get_id())
        else:
            label = str(node.get_name()) if isinstance(node, BPMN.Task) else None
            if not label:
                label = None
        transition = PetriNet.Transition(name=str(node.get_id()), label=label)
        net.transitions.add(transition)
        add_arc_from_to(entry_place, transition, net)
        add_arc_from_to(transition, exiting_place, net)

        if isinstance(node, BPMN.ParallelGateway) or isinstance(node, BPMN.InclusiveGateway):
            if source_count[node] > 1:
                exiting_object = PetriNet.Transition(str(uuid.uuid4()), None)
                net.transitions.add(exiting_object)
                add_arc_from_to(exiting_place, exiting_object, net)
            else:
                exiting_object = exiting_place

            if target_count[node] > 1:
                entering_object = PetriNet.Transition(str(uuid.uuid4()), None)
                net.transitions.add(entering_object)
                add_arc_from_to(entering_object, entry_place, net)
            else:
                entering_object = entry_place
            nodes_entering[node] = entering_object
            nodes_exiting[node] = exiting_object
        else:
            nodes_entering[node] = entry_place
            nodes_exiting[node] = exiting_place

        if isinstance(node, BPMN.StartEvent):
            start_transition = PetriNet.Transition(str(uuid.uuid4()), None)
            net.transitions.add(start_transition)
            add_arc_from_to(source_place, start_transition, net)
            add_arc_from_to(start_transition, entry_place, net)
        elif isinstance(node, BPMN.EndEvent):
            end_transition = PetriNet.Transition(str(uuid.uuid4()), None)
            net.transitions.add(end_transition)
            add_arc_from_to(exiting_place, end_transition, net)
            add_arc_from_to(end_transition, sink_place, net)

    for flow in bpmn_graph.get_flows():
        source_object = nodes_exiting[flow.get_source()]
        target_object = nodes_entering[flow.get_target()]

        if isinstance(source_object, PetriNet.Place):
            inv1 = PetriNet.Transition(str(uuid.uuid4()), None)
            net.transitions.add(inv1)
            add_arc_from_to(source_object, inv1, net)
            source_object = inv1

        if isinstance(target_object, PetriNet.Place):
            inv2 = PetriNet.Transition(str(uuid.uuid4()), None)
            net.transitions.add(inv2)
            add_arc_from_to(inv2, target_object, net)
            target_object = inv2

        add_arc_from_to(source_object, flow_place[flow], net)
        add_arc_from_to(flow_place[flow], target_object, net)

    if inclusive_gateway_exit and inclusive_gateway_entry:
        # do the following steps if there are inclusive gateways:
        # - calculate the shortest paths
        # - add an invisible transition between couples of corresponding places
        # this ensures soundness and the correct translation of the BPMN
        inv_places = {x.name: x for x in net.places}
        digraph = build_digraph_from_petri_net(net)
        all_shortest_paths = dict(nx.all_pairs_dijkstra(digraph))
        keys = list(all_shortest_paths.keys())

        for pl1 in inclusive_gateway_exit:
            if pl1 in keys:
                output_places = sorted(
                    [(x, len(y)) for x, y in all_shortest_paths[pl1][1].items() if x in inclusive_gateway_entry],
                    key=lambda x: x[1])
                if output_places:
                    inv_trans = PetriNet.Transition(str(uuid.uuid4()), None)
                    net.transitions.add(inv_trans)
                    add_arc_from_to(inv_places[pl1], inv_trans, net)
                    add_arc_from_to(inv_trans, inv_places[output_places[0][0]], net)

    reduction.apply_simple_reduction(net)

    return net, im, fm
