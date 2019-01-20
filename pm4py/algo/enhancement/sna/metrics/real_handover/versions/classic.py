from pm4py.algo.enhancement.sna.transformer.common import rscrsc as rscrsc_utils


def apply(mco, parameters=None):
    """
    Calculate the Real Handover of Work metric

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

    dependency_threshold = parameters["dependency_threshold"] if "dependency_threshold" in parameters else 0

    if len(mco.activities_list) == 0:
        raise Exception("must provide full MCO dataframe")

    rsc_rsc_matrix = rscrsc_utils.get_empty_rscrsc_matrix(mco)

    grouped_activity_paris = mco.dataframe.groupby(['activity', 'next_activity']).size().reset_index(
        name='counts')

    for index, row in mco.dataframe.iterrows():
        ab = grouped_activity_paris.loc[(grouped_activity_paris['activity'] == row['activity']) & (
                grouped_activity_paris['next_activity'] == row['next_activity'])]
        if ab.empty:
            abn = 0
        else:
            abn = ab.iloc[0, 2]
        ba = grouped_activity_paris.loc[(grouped_activity_paris['next_activity'] == row['activity']) & (
                grouped_activity_paris['activity'] == row['next_activity'])]
        if ba.empty:
            ban = 0
        else:
            ban = ab.iloc[0, 2]
        if row['activity'] == row['next_activity']:
            dependency = abn / (abn + 1)
        else:
            dependency = (abn - ban) / (abn + ban + 1)

        if dependency > dependency_threshold:
            rsc_rsc_matrix[mco.resources_list.index(row['resource'])][
                mco.resources_list.index(row['next_resource'])] += 1

    return rsc_rsc_matrix
