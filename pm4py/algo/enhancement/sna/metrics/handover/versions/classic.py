from pm4py.algo.enhancement.sna.transformer.common import rscrsc as rscrsc_utils


def apply(mco, parameters=None):
    """
    Calculate the Handover of Work metric

    Parameters
    ------------
    mco
        Matrix container object
    parameters
        Parameters of the algorithm

    Returns
    ------------
    rsc_rsc_matrix
        Resource-Resource Matrix containing the Real Handover of Work metric value
    """
    if parameters is None:
        parameters = {}

    rsc_rsc_matrix = rscrsc_utils.get_empty_rscrsc_matrix(mco)

    for resource, next_resource in zip(mco.dataframe['resource'], mco.dataframe['next_resource']):
        rsc_rsc_matrix[mco.resources_list.index(resource)][mco.resources_list.index(next_resource)] += 1

    return rsc_rsc_matrix
