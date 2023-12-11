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
from pm4py.util import exec_utils, pandas_utils
from pm4py.algo.transformation.ocel.graphs import object_interaction_graph, object_descendants_graph, object_cobirth_graph, object_codeath_graph
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from copy import copy
import pandas as pd


class Parameters(Enum):
    INCLUDED_GRAPHS = "included_graphs"


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Inserts the information inferred from the graph computations in the list of O2O relations of the OCEL

    Parameters
    ----------------
    ocel
        Object-centric event log
    parameters
        Possible parameters of the algorithm:
        - Parameters.INCLUDED_GRAPHS => graphs to include in the list of O2O relations
        (object_interaction_graph, object_descendants_graph, object_inheritance_graph, object_cobirth_graph, object_codeath_graph)

    Returns
    ---------------
    enriched_ocel
        Enriched object-centric event log
    """
    if parameters is None:
        parameters = {}

    included_graphs = exec_utils.get_param_value(Parameters.INCLUDED_GRAPHS, parameters, None)
    if included_graphs is None:
        included_graphs = {"object_interaction_graph", "object_descendants_graph", "object_inheritance_graph", "object_cobirth_graph", "object_codeath_graph"}

    o2o = set()

    if "object_interaction_graph" in included_graphs:
        graph = object_interaction_graph.apply(ocel, parameters=parameters)
        for el in graph:
            if el[0] != el[1]:
                o2o.add((el[0], el[1], "object_interaction_graph"))
                o2o.add((el[1], el[0], "object_interaction_graph"))
    if "object_descendants_graph" in included_graphs:
        graph = object_descendants_graph.apply(ocel, parameters=parameters)
        for el in graph:
            o2o.add((el[0], el[1], "object_descendants_graph"))
    if "object_inheritance_graph" in included_graphs:
        graph = object_descendants_graph.apply(ocel, parameters=parameters)
        for el in graph:
            o2o.add((el[0], el[1], "object_inheritance_graph"))
    if "object_cobirth_graph" in included_graphs:
        graph = object_cobirth_graph.apply(ocel, parameters=parameters)
        for el in graph:
            o2o.add((el[0], el[1], "object_cobirth_graph"))
    if "object_codeath_graph" in included_graphs:
        graph = object_codeath_graph.apply(ocel, parameters=parameters)
        for el in graph:
            o2o.add((el[0], el[1], "object_codeath_graph"))

    o2o = [{ocel.object_id_column: x[0], ocel.object_id_column+"_2": x[1], ocel.qualifier: x[2]} for x in o2o]
    ocel = copy(ocel)
    o2o = pandas_utils.instantiate_dataframe(o2o)
    ocel.o2o = pandas_utils.concat([ocel.o2o, o2o])

    return ocel
