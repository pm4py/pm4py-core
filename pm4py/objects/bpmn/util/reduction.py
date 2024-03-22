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
from pm4py.objects.bpmn.obj import BPMN


def reduce_xor_gateways(bpmn_graph, parameters=None):
    """
    Reduces the number of XOR gateways in the diagram

    Parameters
    ------------
    bpmn_graph
        BPMN graph
    parameters
        Parameters

    Returns
    ------------
    bpmn_graph
        (possibly reduced) BPMN graph
    """
    if parameters is None:
        parameters = {}

    changed = True
    while changed:
        changed = False
        outgoing_edges = None
        incoming_edges = None
        outgoing_edges = {}
        incoming_edges = {}

        for flow in bpmn_graph.get_flows():
            source = flow.get_source()
            target = flow.get_target()

            if source not in outgoing_edges:
                outgoing_edges[source] = set()
            outgoing_edges[source].add(flow)

            if target not in incoming_edges:
                incoming_edges[target] = set()
            incoming_edges[target].add(flow)

        nodes = list(bpmn_graph.get_nodes())
        for node in nodes:
            if isinstance(node, BPMN.ExclusiveGateway):
                if node in outgoing_edges and node in incoming_edges and len(outgoing_edges[node]) == 1 and len(
                        incoming_edges[node]) == 1:
                    changed = True
                    source_node = None
                    target_node = None
                    for flow in incoming_edges[node]:
                        source_node = flow.get_source()
                        if flow in bpmn_graph.get_flows():
                            bpmn_graph.remove_flow(flow)
                    for flow in outgoing_edges[node]:
                        target_node = flow.get_target()
                        if flow in bpmn_graph.get_flows():
                            bpmn_graph.remove_flow(flow)
                    if node in bpmn_graph.get_nodes():
                        bpmn_graph.remove_node(node)
                    bpmn_graph.add_flow(BPMN.SequenceFlow(source_node, target_node))
                    break

    return bpmn_graph


def apply(bpmn_graph, parameters=None):
    """
    Reduce the complexity of a BPMN graph by removing useless elements

    Parameters
    ------------
    bpmn_graph
        BPMN graph
    parameters
        Parameters

    Returns
    ------------
    bpmn_graph
        (possibly reduced) BPMN graph
    """
    if parameters is None:
        parameters = {}

    bpmn_graph = reduce_xor_gateways(bpmn_graph, parameters=parameters)
    return bpmn_graph
