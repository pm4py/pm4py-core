import numpy as np
import pandas as pd
from _collections import defaultdict

from pm4py.algo.enhancement.sna.transformer.common import rscact as rscact_utils
from pm4py.algo.enhancement.sna.transformer.common import rscrsc as rscrsc_utils
from scipy.stats import pearsonr


def apply(mco, parameters=None):
    """
    Calculate the Similar Activities metric

    Parameters
    ------------
    mco
        Matrix container object
    parameters
        Parameters of the algorithm

    Returns
    ------------
    rsc_rsc_matrix
        Resource-Resource Matrix containing the Similar Activities metric value
    """
    if parameters is None:
        parameters = {}
    
    if len(mco.activities_list) == 0:
        raise Exception("must provide full MCO dataframe")

    all_resources = np.concatenate([mco.dataframe['resource'], mco.dataframe['next_resource']], axis=0)
    all_activities = np.concatenate([mco.dataframe['activity'], mco.dataframe['next_activity']], axis=0)

    all_resource_activity = np.concatenate(
        [all_resources.reshape(len(all_resources), 1), all_activities.reshape(len(all_activities), 1)], axis=1)
    all_resource_activity_df = pd.DataFrame(columns=['resource', 'activity'],
                                            data=all_resource_activity)

    grouped_by_activity = all_resource_activity_df.groupby(['resource'])
    resource_activity_dict = defaultdict(list)

    for resource, group in grouped_by_activity:
        resource_activity_dict[resource].append(group[
                                                    'activity'].values)

    rsc_act_matrix = rscact_utils.get_empty_rscact_matrix(mco)

    for resource in resource_activity_dict:
        for activity_list in resource_activity_dict[resource]:
            for activity in activity_list:
                rsc_act_matrix[mco.resources_list.index(resource)][mco.activities_list.index(activity)] += 1

    rsc_rsc_matrix = rscrsc_utils.get_empty_rscrsc_matrix(mco)
    for index, resource in enumerate(rsc_act_matrix):
        for rest in range(index + 1, rsc_act_matrix.shape[0]):
            main_resource = resource
            other_resource = rsc_act_matrix[rest]
            r, p = pearsonr(main_resource, other_resource)
            rsc_rsc_matrix[index][rest] = r

    return rsc_rsc_matrix
