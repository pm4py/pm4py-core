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
