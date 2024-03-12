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
from pm4py.util import nx_utils
from typing import Optional, Dict, Any
from pm4py.algo.transformation.ocel.graphs import object_interaction_graph


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Adds for each object the centrality degree as feature

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

    g0 = object_interaction_graph.apply(ocel, parameters=parameters)
    g = nx_utils.Graph()
    for edge in g0:
        g.add_edge(edge[0], edge[1])

    centrality = nx_utils.degree_centrality(g)

    data = []
    feature_names = ["@@object_degree_centrality"]

    for obj in ordered_objects:
        if obj in centrality:
            data.append([float(centrality[obj])])
        else:
            data.append([0.0])

    return data, feature_names
