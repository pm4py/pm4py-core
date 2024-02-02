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
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.util import exec_utils, nx_utils
from pm4py.algo.transformation.ocel.graphs import object_interaction_graph, object_descendants_graph, object_inheritance_graph, object_cobirth_graph, object_codeath_graph


class Parameters(Enum):
    INCLUDE_OBJ_INTERACTION_GRAPH = "include_obj_interaction_graph"
    INCLUDE_OBJ_DESCENDANTS_GRAPH = "include_obj_descendants_graph"
    INCLUDE_OBJ_INHERITANCE_GRAPH = "include_obj_inheritance_graph"
    INCLUDE_OBJ_COBIRTH_GRAPH = "include_obj_cobirth_graph"
    INCLUDE_OBJ_CODEATH_GRAPH = "include_obj_codeath_graph"


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]]=None):
    """
    Converts the graphs of features extracted from an OCEL to a NetworkX DiGraph object

    Parameters
    --------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.INCLUDE_OBJ_INTERACTION_GRAPH => includes the object interaction graph in the NX DiGraph
        - Parameters.INCLUDE_OBJ_DESCENDANTS_GRAPH => includes the object descendants graph in the NX DiGraph
        - Parameters.INCLUDE_OBJ_INHERITANCE_GRAPH => includes the object inheritance graph in the NX DiGraph
        - Parameters.INCLUDE_OBJ_COBIRTH_GRAPH => includes the object cobirth graph in the NX DiGraph
        - Parameters.INCLUDE_OBJ_CODEATH_GRAPH => includes the object codeath graph in the NX DiGraph

    Returns
    -------------
    G
        NetworkX DiGraph
    """
    if parameters is None:
        parameters = {}

    include_obj_interaction_graph = exec_utils.get_param_value(Parameters.INCLUDE_OBJ_INTERACTION_GRAPH, parameters, True)
    include_obj_descendants_graph = exec_utils.get_param_value(Parameters.INCLUDE_OBJ_DESCENDANTS_GRAPH, parameters, True)
    include_obj_inheritance_graph = exec_utils.get_param_value(Parameters.INCLUDE_OBJ_INHERITANCE_GRAPH, parameters, True)
    include_obj_cobirth_graph = exec_utils.get_param_value(Parameters.INCLUDE_OBJ_COBIRTH_GRAPH, parameters, True)
    include_obj_codeath_graph = exec_utils.get_param_value(Parameters.INCLUDE_OBJ_CODEATH_GRAPH, parameters, True)

    G = nx_utils.DiGraph()
    if include_obj_interaction_graph:
        interaction_graph = object_interaction_graph.apply(ocel, parameters=parameters)
        G.add_edges_from(interaction_graph, attr={"type": "INTERACTION"})

    if include_obj_descendants_graph:
        descendants_graph = object_descendants_graph.apply(ocel, parameters=parameters)
        G.add_edges_from(descendants_graph, attr={"type": "DESCENDANTS"})

    if include_obj_inheritance_graph:
        inheritance_graph =  object_inheritance_graph.apply(ocel, parameters=parameters)
        G.add_edges_from(inheritance_graph, attr={"type": "INHERITANCE"})

    if include_obj_cobirth_graph:
        cobirth_graph = object_cobirth_graph.apply(ocel, parameters=parameters)
        G.add_edges_from(cobirth_graph, attr={"type": "COBIRTH"})

    if include_obj_codeath_graph:
        codeath_graph = object_codeath_graph.apply(ocel, parameters=parameters)
        G.add_edges_from(codeath_graph, attr={"type": "CODEATH"})

    return G
