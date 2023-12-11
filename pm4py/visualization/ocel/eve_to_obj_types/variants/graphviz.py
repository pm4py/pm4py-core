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
from enum import Enum
from pm4py.util import exec_utils, vis_utils, constants
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from graphviz import Digraph
import tempfile
import uuid


class Parameters(Enum):
    FORMAT = "format"
    BGCOLOR = "bgcolor"
    RANKDIR = "rankdir"
    ANNOTATE_FREQUENCY = "annotate_frequency"


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Digraph:
    """
    Shows the relationships between the different event and object types of the
    object-centric event log.

    Parameters
    ---------------
    ocel
        Object-centric event log
    parameters
        Parameters of the visualization, including:
        - Parameters.FORMAT => format of the visualization (.png, .svg)
        - Parameters.BGCOLOR => background color of the visualization (transparent, white)
        - Parameters.RANKDIR => direction of the graph (LR or TB)
        - Parameters.ANNOTATE_FREQUENCY => annotate the frequency on the arcs

    Returns
    --------------
    gviz
        Graphviz object
    """
    if parameters is None:
        parameters = {}

    format = exec_utils.get_param_value(Parameters.FORMAT, parameters, constants.DEFAULT_FORMAT_GVIZ_VIEW)
    bgcolor = exec_utils.get_param_value(Parameters.BGCOLOR, parameters, constants.DEFAULT_BGCOLOR)
    rankdir = exec_utils.get_param_value(Parameters.RANKDIR, parameters, "LR")
    annotate_frequency = exec_utils.get_param_value(Parameters.ANNOTATE_FREQUENCY, parameters, False)

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph("eve_to_obj_types", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor})

    event_types = sorted(list(ocel.events[ocel.event_activity].unique()))
    object_types = sorted(list(ocel.objects[ocel.object_type_column].unique()))
    ev_to_obj_types = ocel.relations.groupby([ocel.event_activity, ocel.object_type_column]).size().to_dict()

    min_num = min(ev_to_obj_types.values())
    max_num = max(ev_to_obj_types.values())

    ev_types_dict = {e: str(uuid.uuid4()) for e in event_types}
    obj_types_dict = {o: str(uuid.uuid4()) for o in object_types}

    for ev in event_types:
        viz.node(ev_types_dict[ev], ev, style="filled", fillcolor="pink", shape='ellipse')

    for obj in object_types:
        viz.node(obj_types_dict[obj], obj, style="filled", fillcolor="lightblue", shape='box')

    for arc in ev_to_obj_types:
        label = " "
        if annotate_frequency:
            label = str(ev_to_obj_types[arc])
        viz.edge(ev_types_dict[arc[0]], obj_types_dict[arc[1]], label=label, penwidth=str(vis_utils.get_arc_penwidth(ev_to_obj_types[arc], min_num, max_num)))

    viz.attr(rankdir=rankdir)
    viz.format = format.replace("html", "plain-ext")

    return viz
