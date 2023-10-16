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
from typing import Optional, Dict, Any, Set, Tuple
from graphviz import Digraph, Graph
from enum import Enum
from pm4py.util import exec_utils
import tempfile
from pm4py.util import vis_utils, constants
from pm4py.objects.ocel.obj import OCEL


class Parameters(Enum):
    FORMAT = "format"
    BGCOLOR = "bgcolor"
    RANKDIR = "rankdir"
    DIRECTED = "directed"


def ot_to_color(ot: str) -> str:
    ot = int(hash(ot))
    num = []
    while len(num) < 6:
        num.insert(0, ot % 16)
        ot = ot // 16
    ret = "#" + "".join([vis_utils.get_corr_hex(x) for x in num])
    return ret


def apply(ocel: OCEL, graph: Set[Tuple[str, str]], parameters: Optional[Dict[Any, Any]] = None) -> Digraph:
    """
    Visualizes an object graph

    Parameters
    -------------
    ocel
        Object-centric event log
    graph
        Object graph
    parameters
        Variant-specific parameters:
            - Parameters.FORMAT => the format of the visualization ("png", "svg", ...)
            - Parameters.BGCOLOR => the background color
            - Parameters.RANKDIR => the rank direction (LR = left-right, TB = top-bottom)
            - Parameters.DIRECTED => boolean value (draws a directed or undirected graph)

    Returns
    -------------
    gviz
        Graphviz object
    """
    if parameters is None:
        parameters = {}

    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    bgcolor = exec_utils.get_param_value(Parameters.BGCOLOR, parameters, "transparent")
    rankdir = exec_utils.get_param_value(Parameters.RANKDIR, parameters, constants.DEFAULT_RANKDIR_GVIZ)
    directed = exec_utils.get_param_value(Parameters.DIRECTED, parameters, True)

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    filename.close()

    if directed:
        viz = Digraph("ograph", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor})
    else:
        viz = Graph("ograph", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor})
    viz.attr('node', shape='ellipse', fixedsize='false')

    ob_type = ocel.objects.groupby(ocel.object_id_column).first()[ocel.object_type_column].to_dict()

    nodes = set(x[0] for x in graph).union(set(x[1] for x in graph))
    nodes_dict = {}
    for n in nodes:
        v = str(uuid.uuid4())
        nodes_dict[n] = v
        viz.node(v, label=n, fontcolor=ot_to_color(ob_type[n]), color=ot_to_color(ob_type[n]))

    for e in graph:
        viz.edge(nodes_dict[e[0]], nodes_dict[e[1]])

    viz.attr(rankdir=rankdir)
    viz.format = image_format.replace("html", "plain-ext")

    return viz
