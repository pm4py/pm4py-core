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
import os

from pm4py.objects.powl.obj import POWL
from pm4py.util import exec_utils
from enum import Enum
import tempfile
import importlib.resources
import graphviz
from graphviz import Digraph
from typing import Optional, Dict, Any
from pm4py.util import constants
from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.bpmn.util.sorting import get_sorted_nodes_edges
from pm4py.objects.conversion.powl.converter import apply as powl_to_pn
from pm4py.objects.bpmn.util import reduction


class Parameters(Enum):
    FORMAT = "format"
    RANKDIR = "rankdir"
    FONT_SIZE = "font_size"
    BGCOLOR = "bgcolor"


FREQUENCY_TAGS_BORDER = False


class SplitExclusiveGateway(BPMN.ExclusiveGateway):
    pass


class JoinExclusiveGateway(BPMN.ExclusiveGateway):
    pass


def can_connect_without_xor_violation(input_nodes, output_nodes):
    for in_node in input_nodes:
        for out_node in output_nodes:
            if isinstance(in_node, BPMN.ExclusiveGateway) and len(output_nodes) > 1:
                return False
            if isinstance(out_node, BPMN.ExclusiveGateway) and len(input_nodes) > 1:
                return False

    return True


def simplify_and_gateways(nodes, edges):
    for n in nodes:
        if isinstance(n, BPMN.ParallelGateway):
            input_nodes = [edge[0] for edge in edges if edge[1] == n]
            output_nodes = [edge[1] for edge in edges if edge[0] == n]
            if can_connect_without_xor_violation(input_nodes, output_nodes):
                nodes.remove(n)
                edges = [edge for edge in edges if n not in edge]

                for in_node in input_nodes:
                    for out_node in output_nodes:
                        edges.append((in_node, out_node))
                return simplify_and_gateways(nodes, edges)

    return nodes, edges


def add_node(n, viz, parameters):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    font_size = exec_utils.get_param_value(Parameters.FONT_SIZE, parameters, "16")
    n_id = str(id(n))
    if isinstance(n, FrequencyTask):
        if FREQUENCY_TAGS_BORDER:
            peripheries = '1'
            if n.selfloop:
                peripheries = '2'
            if n.skippable:
                viz.node(n_id, shape="box", label=n.activity, fontsize=font_size, peripheries=peripheries,
                         style="dashed")
            else:
                viz.node(n_id, shape="box", label=n.activity, fontsize=font_size, peripheries=peripheries)
        else:
            label = n.activity
            if n.skippable:
                label = label + "\n?"
                if n.selfloop:
                    label = label + "*"
            elif n.selfloop:
                label = label + "\n*"
            viz.node(n_id, shape="box", label=label, fontsize=font_size)
    elif isinstance(n, BPMN.StartEvent):
        with importlib.resources.path("pm4py.visualization.powl.variants", "play.png") as gimg:
            viz.node(n_id, image=str(gimg), label="", shape="none", width='0.35',
                     height='0.35', fixedsize="true")
    elif isinstance(n, BPMN.EndEvent):
        with importlib.resources.path("pm4py.visualization.powl.variants", "end.png") as gimg:
            viz.node(n_id, image=str(gimg), label="", shape="none", width='0.35',
                     height='0.35', fixedsize="true")
    elif isinstance(n, BPMN.ParallelGateway):
        viz.node(n_id, label="", shape="square", fontsize=font_size, style="filled", fillcolor="black", width='0.3',
                 height='0.3')
    elif isinstance(n, SplitExclusiveGateway):
        viz.node(n_id, label="", shape="diamond", style="filled", fillcolor="lightgreen", fontsize=font_size,
                 width='0.4', height='0.4')
    elif isinstance(n, JoinExclusiveGateway):
        viz.node(n_id, label="", shape="diamond", style="filled", fillcolor="orange", fontsize=font_size,
                 width='0.4', height='0.4')
    elif isinstance(n, BPMN.ExclusiveGateway):
        viz.node(n_id, label="", shape="diamond", fontsize=font_size,
                 width='0.4', height='0.4')
    else:
        raise Exception("Unexpected instance of class " + str(type(n)) + "!")


def apply(powl: POWL, parameters: Optional[Dict[Any, Any]] = None) -> graphviz.Digraph:
    pn_2, init_2, final_2 = powl_to_pn(powl)
    bpmn_graph = to_bpmn(pn_2, init_2, final_2)

    nodes, edges = get_sorted_nodes_edges(bpmn_graph)

    for node in nodes:

        if isinstance(node, BPMN.ExclusiveGateway):

            incoming_edges = [e[0] for e in edges if e[1] is node]
            outgoing_edges = [e[1] for e in edges if e[0] is node]

            if len(incoming_edges) == 1 and len(outgoing_edges) > 1:

                node.__class__ = SplitExclusiveGateway

            elif len(incoming_edges) > 1 and len(outgoing_edges) == 1:

                node.__class__ = JoinExclusiveGateway

    nodes, edges = simplify_and_gateways(nodes, edges)

    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    rankdir = exec_utils.get_param_value(Parameters.RANKDIR, parameters, "LR")

    bgcolor = exec_utils.get_param_value(Parameters.BGCOLOR, parameters, constants.DEFAULT_BGCOLOR)

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph("", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor})
    viz.graph_attr['rankdir'] = rankdir

    gateway_edges = {}

    for e in edges:
        if isinstance(e[0], BPMN.ParallelGateway) or isinstance(e[0], BPMN.ParallelGateway):
            if e[0] not in gateway_edges:
                gateway_edges[e[0]] = {'in': [], 'out': []}
            gateway_edges[e[0]]['out'].append(e[1])
            continue
        if isinstance(e[1], BPMN.ParallelGateway) or isinstance(e[1], BPMN.ParallelGateway):
            if e[1] not in gateway_edges:
                gateway_edges[e[1]] = {'in': [], 'out': []}
            gateway_edges[e[1]]['in'].append(e[0])
            continue

    for node in nodes:
        add_node(node, viz, parameters)
    add_concurrent_subgraphs(viz, find_concurrent_groups(nodes, edges))

    for e in edges:
        n_id_1 = str(id(e[0]))
        n_id_2 = str(id(e[1]))

        viz.edge(n_id_1, n_id_2)

    viz.attr(overlap='false')

    viz.format = image_format

    return viz


class FrequencyTask(BPMN.Task):
    def __init__(self, name, properties, id="", in_arcs=None, out_arcs=None, process=None):
        super().__init__(id=id, name=name, in_arcs=in_arcs, out_arcs=out_arcs, process=process)
        self.activity = properties["activity"]
        self.skippable = properties["skippable"]
        self.selfloop = properties["selfloop"]


def to_bpmn(net, im, fm):
    """
    Converts an accepting Petri net into a BPMN diagram

    Parameters
    --------------
    net
        Petri net
    im
        initial marking
    fm
        final marking

    Returns
    --------------
    bpmn_graph
        BPMN diagram
    """

    bpmn_graph = BPMN()

    entering_dictio = {}
    exiting_dictio = {}

    for place in net.places:
        node = BPMN.ExclusiveGateway()
        bpmn_graph.add_node(node)
        entering_dictio[place] = node
        exiting_dictio[place] = node

    for trans in net.transitions:
        if trans.label is None:
            if len(trans.in_arcs) > 1:
                node = BPMN.ParallelGateway(gateway_direction=BPMN.Gateway.Direction.CONVERGING)
            elif len(trans.out_arcs) > 1:
                node = BPMN.ParallelGateway(gateway_direction=BPMN.Gateway.Direction.DIVERGING)
            else:
                node = BPMN.ExclusiveGateway(gateway_direction=BPMN.Gateway.Direction.UNSPECIFIED)
            bpmn_graph.add_node(node)
            entering_dictio[trans] = node
            exiting_dictio[trans] = node
        else:
            if len(trans.in_arcs) > 1:
                entering_node = BPMN.ParallelGateway(gateway_direction=BPMN.Gateway.Direction.CONVERGING)
            else:
                entering_node = BPMN.ExclusiveGateway(gateway_direction=BPMN.Gateway.Direction.UNSPECIFIED)

            if len(trans.out_arcs) > 1:
                exiting_node = BPMN.ParallelGateway(gateway_direction=BPMN.Gateway.Direction.DIVERGING)
            else:
                exiting_node = BPMN.ExclusiveGateway(gateway_direction=BPMN.Gateway.Direction.UNSPECIFIED)

            task = FrequencyTask(name=trans.label, properties=trans.properties)
            bpmn_graph.add_node(task)

            bpmn_graph.add_flow(BPMN.Flow(entering_node, task))
            bpmn_graph.add_flow(BPMN.Flow(task, exiting_node))

            entering_dictio[trans] = entering_node
            exiting_dictio[trans] = exiting_node

    for arc in net.arcs:
        bpmn_graph.add_flow(BPMN.Flow(exiting_dictio[arc.source], entering_dictio[arc.target]))

    start_node = BPMN.StartEvent(name="start", isInterrupting=True)
    end_node = BPMN.NormalEndEvent(name="end")
    bpmn_graph.add_node(start_node)
    bpmn_graph.add_node(end_node)
    for place in im:
        bpmn_graph.add_flow(BPMN.Flow(start_node, entering_dictio[place]))
    for place in fm:
        bpmn_graph.add_flow(BPMN.Flow(exiting_dictio[place], end_node))

    bpmn_graph = reduction.apply(bpmn_graph)

    for node in bpmn_graph.get_nodes():
        node.set_process(bpmn_graph.get_process_id())

    for edge in bpmn_graph.get_flows():
        edge.set_process(bpmn_graph.get_process_id())

    return bpmn_graph


def find_concurrent_groups(nodes, edges):
    predecessors = {n: [] for n in nodes}
    successors = {n: [] for n in nodes}
    for src, dst in edges:
        successors[src].append(dst)
        predecessors[dst].append(src)

    groups = {}
    for node, preds in predecessors.items():
        if len(preds) == 1:
            pred_id = str(id(preds[0]))
            if pred_id not in groups:
                groups[pred_id] = []
            groups[pred_id].append(node)

    return [group for group in groups.values() if len(group) > 1]


def add_concurrent_subgraphs(graph, concurrent_elements):
    for group in concurrent_elements:
        with graph.subgraph() as s:
            s.attr(rank='same')
            for n in group:
                s.node(str(id(n)))
