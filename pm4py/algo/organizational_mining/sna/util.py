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
from typing import List, Dict
from enum import Enum
from pm4py.util import exec_utils, nx_utils
from pm4py.objects.org.sna.obj import SNA
import numpy as np


class Parameters(Enum):
    WEIGHT_THRESHOLD = "weight_threshold"


def sna_result_to_nx_graph(sna: SNA, parameters=None):
    """
    Transforms the results of SNA to a NetworkX Graph / DiGraph object
    (depending on the type of analysis).

    Parameters
    ------------------
    sna
        Result of a SNA operation
    parameters
        Parameters of the algorithm, including:
        - Parameters.WEIGHT_THRESHOLD => the weight threshold (used to filter out edges)

    Returns
    -----------------
    nx_graph
        NetworkX Graph / DiGraph
    """
    if parameters is None:
        parameters = {}

    weight_threshold = exec_utils.get_param_value(Parameters.WEIGHT_THRESHOLD, parameters, 0.0)
    directed = sna.is_directed

    if directed:
        graph = nx_utils.DiGraph()
    else:
        graph = nx_utils.Graph()

    graph.add_edges_from({c for c, w in sna.connections.items() if w >= weight_threshold})

    return graph


def cluster_affinity_propagation(sna: SNA, parameters=None) -> Dict[str, List[str]]:
    """
    Performs a clustering using the affinity propagation algorithm provided by Scikit Learn

    Parameters
    --------------
    sna
        Result of a SNA operation
    parameters
        Parameters of the algorithm

    Returns
    --------------
    clustering
        Dictionary that contains, for each cluster that has been identified,
        the list of resources of the cluster
    """
    from pm4py.util import ml_utils

    if parameters is None:
        parameters = {}

    originators = list(set(x[0] for x, y in sna.connections.items()).union(set(x[1] for x, y in sna.connections.items())))
    matrix = np.zeros((len(originators), len(originators)))
    for c, w in sna.connections.items():
        matrix[originators.index(c[0]), originators.index(c[1])] = w

    affinity_propagation = ml_utils.AffinityPropagation(**parameters)
    affinity_propagation.fit(matrix)

    clusters = affinity_propagation.predict(matrix)
    ret = {}
    for i in range(len(clusters)):
        res = originators[i]
        cluster = str(clusters[i])
        if cluster not in ret:
            ret[cluster] = []
        ret[cluster].append(res)

    return ret
