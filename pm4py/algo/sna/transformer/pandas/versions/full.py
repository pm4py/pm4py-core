import pandas as pd

from pm4py.algo.sna.transformer.common import df_utilities
from pm4py.objects.log.util import xes
from pm4py.objects.sna.matrix_container import MatrixContainer
from pm4py.util import constants


def apply(df, parameters=None):
    """
    Create full matrix (containing resources and activities) from the Pandas dataframe

    Parameters
    ------------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm

    Returns
    ------------
    mco
        SNA Matrix container object
    """
    if parameters is None:
        parameters = {}

    resource_key = parameters[
        constants.PARAMETER_CONSTANT_RESOURCE_KEY] if constants.PARAMETER_CONSTANT_RESOURCE_KEY in parameters else xes.DEFAULT_RESOURCE_KEY
    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    case_id_glue = parameters[
        constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else "case:concept:name"

    df_reduced = df[[case_id_glue, activity_key, resource_key]]
    # shift the dataframe by 1, in order to couple successive rows
    df_reduced_shifted = df_reduced.shift(-1)
    # change column names to shifted dataframe
    df_reduced_shifted.columns = [str(col) + '_2' for col in df_reduced_shifted.columns]
    # concate the two dataframe to get a unique dataframe
    full_df = pd.concat([df_reduced, df_reduced_shifted], axis=1)
    # as successive rows in the sorted dataframe may belong to different case IDs we have to restrict ourselves to
    # successive rows belonging to same case ID
    full_df = full_df[full_df[case_id_glue] == full_df[case_id_glue + '_2']]

    full_df = \
    full_df.rename(columns={resource_key: "resource", resource_key + '_2': "next_resource", activity_key: "activity",
                            activity_key + '_2': "next_activity"})[
        ["resource", "activity", "next_resource", "next_activity"]]

    resources_set = df_utilities.get_resources_from_df(full_df)
    activities_set = df_utilities.get_activities_from_df(full_df)

    mco = MatrixContainer(full_df, resources_set, activities_set)

    return mco
