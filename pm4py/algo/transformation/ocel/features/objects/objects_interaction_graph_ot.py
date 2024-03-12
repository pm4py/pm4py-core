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
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.algo.transformation.ocel.graphs import object_interaction_graph
from pm4py.util import pandas_utils


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Adds for each object, and each object type, the number of interacting objects as a feature.

    Parameters
    -----------------
    ocel
        OCEL
    parameters
        Parameters of the algorithm

    Returns
    -----------------
    data
        Values of the added features
    feature_names
        Names of the added features
    """
    if parameters is None:
        parameters = {}

    ordered_objects = parameters["ordered_objects"] if "ordered_objects" in parameters else ocel.objects[
        ocel.object_id_column].to_numpy()

    object_types = pandas_utils.format_unique(ocel.objects[ocel.object_type_column].unique())

    object_type_association = ocel.objects[[ocel.object_id_column, ocel.object_type_column]].to_dict("records")
    object_type_association = {x[ocel.object_id_column]: x[ocel.object_type_column] for x in object_type_association}

    g0 = object_interaction_graph.apply(ocel, parameters=parameters)
    conn = {}

    for obj in ordered_objects:
        conn[obj] = set()

    for el in g0:
        conn[el[0]].add(el[1])
        conn[el[1]].add(el[0])

    data = []
    feature_names = ["@@object_interaction_graph_"+ot for ot in object_types]

    for obj in ordered_objects:
        data.append([])
        for ot in object_types:
            cot = [x for x in conn[obj] if object_type_association[x] == ot]
            data[-1].append(float(len(cot)))

    return data, feature_names
