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
from typing import Optional, Dict, Any
from graphviz import Digraph
from enum import Enum
from pm4py.util import exec_utils
import tempfile
from pm4py.util import vis_utils
from pm4py.objects.petri_net.obj import PetriNet


class Parameters(Enum):
    FORMAT = "format"
    BGCOLOR = "bgcolor"
    RANKDIR = "rankdir"


def ot_to_color(ot: str) -> str:
    ot = int(hash(ot))
    num = []
    while len(num) < 6:
        num.insert(0, ot % 16)
        ot = ot // 16
    ret = "#" + "".join([vis_utils.get_corr_hex(x) for x in num])
    return ret


def apply(ocpn: Dict[str, Any], parameters: Optional[Dict[Any, Any]] = None) -> Digraph:
    """
    Obtains a visualization of the provided object-centric Petri net (without decoration).

    Reference paper: van der Aalst, Wil MP, and Alessandro Berti. "Discovering object-centric Petri nets." Fundamenta informaticae 175.1-4 (2020): 1-40.

    Parameters
    ----------------
    ocpn
        Object-centric Petri net
    variant
        Variant of the algorithm to be used
    parameters
        Variant-specific parameters:
        - Parameters.FORMAT => the format of the visualization ("png", "svg", ...)
        - Parameters.BGCOLOR => the background color
        - Parameters.RANKDIR => the rank direction (LR = left-right, TB = top-bottom)

    Returns
    ---------------
    gviz
        Graphviz digraph
    """
    if parameters is None:
        parameters = {}

    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    bgcolor = exec_utils.get_param_value(Parameters.BGCOLOR, parameters, "transparent")
    rankdir = exec_utils.get_param_value(Parameters.RANKDIR, parameters, "LR")

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph("ocdfg", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor})
    viz.attr('node', shape='ellipse', fixedsize='false')

    activities_map = {}
    source_places = {}
    target_places = {}
    transition_map = {}
    places = {}

    for act in ocpn["activities"]:
        activities_map[act] = str(uuid.uuid4())
        viz.node(activities_map[act], label=act, shape="box")

    for ot in ocpn["object_types"]:
        otc = ot_to_color(ot)
        source_places[ot] = str(uuid.uuid4())
        target_places[ot] = str(uuid.uuid4())
        viz.node(source_places[ot], label=ot, shape="ellipse", style="filled", fillcolor=otc)
        viz.node(target_places[ot], label=ot, shape="underline", fontcolor=otc)

    for ot in ocpn["petri_nets"]:
        otc = ot_to_color(ot)
        net, im, fm = ocpn["petri_nets"][ot]
        for place in net.places:
            if place in im:
                places[place] = source_places[ot]
            elif place in fm:
                places[place] = target_places[ot]
            else:
                places[place] = str(uuid.uuid4())
                viz.node(places[place], label=" ", shape="circle", style="filled", fillcolor=otc)
        for trans in net.transitions:
            if trans.label is not None:
                transition_map[trans] = activities_map[trans.label]
            else:
                transition_map[trans] = str(uuid.uuid4())
                viz.node(transition_map[trans], label=" ", shape="box", style="filled", fillcolor=otc)

        for arc in net.arcs:
            if type(arc.source) is PetriNet.Place:
                is_double = arc.target.label in ocpn["double_arcs_on_activity"][ot] and ocpn["double_arcs_on_activity"][ot][arc.target.label]
                penwidth = "4.0" if is_double else "1.0"
                viz.edge(places[arc.source], transition_map[arc.target], color=otc, penwidth=penwidth)
            elif type(arc.source) is PetriNet.Transition:
                is_double = arc.source.label in ocpn["double_arcs_on_activity"][ot] and ocpn["double_arcs_on_activity"][ot][arc.source.label]
                penwidth = "4.0" if is_double else "1.0"
                viz.edge(transition_map[arc.source], places[arc.target], color=otc, penwidth=penwidth)

    viz.attr(rankdir=rankdir)
    viz.format = image_format

    return viz
