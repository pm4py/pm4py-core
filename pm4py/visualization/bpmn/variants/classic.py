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
from pm4py.util import exec_utils
from enum import Enum
import tempfile
from graphviz import Digraph


class Parameters(Enum):
    FORMAT = "format"
    RANKDIR = "rankdir"


def apply(bpmn_graph, parameters=None):
    """
    Visualize a BPMN graph

    Parameters
    -------------
    bpmn_graph
        BPMN graph
    parameters
        Parameters of the visualization, including:
         - Parameters.FORMAT: the format of the visualization
         - Parameters.RANKDIR: the direction of the representation (default: LR)

    Returns
    ------------
    gviz
        Graphviz representation
    """
    if parameters is None:
        parameters = {}

    from pm4py.objects.bpmn.bpmn_graph import BPMN
    from pm4py.objects.bpmn.util.sorting import get_sorted_nodes_edges

    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    rankdir = exec_utils.get_param_value(Parameters.RANKDIR, parameters, "LR")

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph("", filename=filename.name, engine='dot', graph_attr={'bgcolor': 'transparent'})
    viz.graph_attr['rankdir'] = rankdir

    nodes, edges = get_sorted_nodes_edges(bpmn_graph)

    for n in nodes:
        n_id = str(id(n))
        if isinstance(n, BPMN.Task):
            viz.node(n_id, shape="box", label=n.get_name())
        elif isinstance(n, BPMN.StartEvent):
            viz.node(n_id, label="", shape="circle", style="filled", fillcolor="green")
        elif isinstance(n, BPMN.EndEvent):
            viz.node(n_id, label="", shape="circle", style="filled", fillcolor="orange")
        elif isinstance(n, BPMN.ParallelGateway):
            viz.node(n_id, label="+", shape="diamond")
        elif isinstance(n, BPMN.ExclusiveGateway):
            viz.node(n_id, label="X", shape="diamond")
        elif isinstance(n, BPMN.InclusiveGateway):
            viz.node(n_id, label="O", shape="diamond")
        elif isinstance(n, BPMN.OtherEvent):
            viz.node(n_id, label="", shape="circle")

    for e in edges:
        n_id_1 = str(id(e[0]))
        n_id_2 = str(id(e[1]))

        viz.edge(n_id_1, n_id_2)

    viz.attr(overlap='false')
    viz.attr(fontsize='11')

    viz.format = image_format

    return viz

