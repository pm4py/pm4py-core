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
from typing import List, Any, Dict


def cluster_affinity_propagation(sna_results: List[List[Any]], parameters=None) -> Dict[str, List[str]]:
    """
    Performs a clustering using the affinity propagation algorithm provided by Scikit Learn

    Parameters
    --------------
    sna_results
        Values for a SNA metric
    parameters
        Parameters of the algorithm

    Returns
    --------------
    clustering
        Dictionary that contains, for each cluster that has been identified,
        the list of resources of the cluster
    """
    from sklearn.cluster import AffinityPropagation

    if parameters is None:
        parameters = {}

    matrix = sna_results[0]
    originators = sna_results[1]
    affinity_propagation = AffinityPropagation(**parameters)
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
