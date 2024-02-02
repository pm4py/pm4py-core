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
from pm4py.util import exec_utils, pandas_utils, nx_utils
from enum import Enum
import sys


class Parameters(Enum):
    CENTRALITY_MEASURE = "centrality_measure"
    MAX_VALUE_CENTRALITY = "max_value_centrality"
    ENABLE_PRINTS = "enable_prints"


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Split the OCEL based on the connected components of the object interaction graph.
    It is also possible, to remove the nodes with higher centrality providing a centrality measure
    and a maximum value of this centrality.

    Parameters
    ----------------
    ocel
        OCEL
    parameters
        Parameters of the algorithm, including:
        - Parameters.CENTRALITY_MEASURE => centrality measure
        - Parameters.MAX_VALUE_CENTRALITY => maximum value of centrality

    Returns
    ----------------
    splitted_ocel
        List of OCELs found based on the connected components
    """
    if parameters is None:
        parameters = {}

    centrality_measure = exec_utils.get_param_value(Parameters.CENTRALITY_MEASURE, parameters, None)
    max_value_centrality = exec_utils.get_param_value(Parameters.MAX_VALUE_CENTRALITY, parameters, sys.maxsize)
    enable_prints = exec_utils.get_param_value(Parameters.ENABLE_PRINTS, parameters, False)

    g0 = object_interaction_graph.apply(ocel, parameters=parameters)
    g = nx_utils.Graph()

    for edge in g0:
        g.add_edge(edge[0], edge[1])

    removed_nodes = set()

    if centrality_measure is not None:
        degree_centrality = centrality_measure(g)
        if enable_prints:
            print(sorted([(x, y) for x, y in degree_centrality.items()], key=lambda x: (x[1], x[0]), reverse=True))

        for n in degree_centrality:
            if degree_centrality[n] > max_value_centrality:
                if enable_prints:
                    print("removing", n)
                removed_nodes.add(n)
                g.remove_node(n)

    conn_comp = list(nx_utils.connected_components(g))

    ret = []

    for index, cc in enumerate(conn_comp):
        subocel = OCEL()
        subocel.objects = ocel.objects[ocel.objects[ocel.object_id_column].isin(cc)]
        subocel.relations = ocel.relations[ocel.relations[ocel.object_id_column].isin(cc)]
        included_evs = pandas_utils.format_unique(subocel.relations[ocel.event_id_column].unique())
        subocel.events = ocel.events[ocel.events[ocel.event_id_column].isin(included_evs)]

        ret.append(subocel)

    return ret
