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
from pm4py.algo.transformation.ocel.graphs import object_inheritance_graph


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Adds for each object the total number of inheritance object (they birth when the given object die) as feature

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

    g0 = object_inheritance_graph.apply(ocel, parameters=parameters)

    data = []
    feature_names = ["@@object_general_inheritance_graph_ascendants", "@@object_general_inheritance_graph_descendants"]

    ascendants = {}
    descendants = {}

    for obj in ordered_objects:
        ascendants[obj] = []
        descendants[obj] = []
    for el in g0:
        descendants[el[0]].append(el[1])
        ascendants[el[1]].append(el[0])

    for obj in ordered_objects:
        data.append([float(len(ascendants[obj])), float(len(descendants[obj]))])

    return data, feature_names
