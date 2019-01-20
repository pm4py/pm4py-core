import pandas as pd

from pm4py.algo.enhancement.sna.transformer.common import df_utilities
from pm4py.objects.log.util import xes
from pm4py.objects.sna.matrix_container import MatrixContainer
from pm4py.util import constants


def apply(df, parameters=None):
    """
    Create basic matrix (containing only resources) from the Pandas dataframe

    Parameters
    ------------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm:
            PARAMETER_CONSTANT_RESOURCE_KEY -> attribute key that contains the resource
            PARAMETER_CONSTANT_CASEID_KEY -> attribute key that contains the case ID
            PARAMETER_CONSTANT_TIMESTAMP_KEY -> attribute key that contains the timestamp
            sort_caseid_required -> Specify if a sort on the Case ID is required
            sort_timestamp_along_case_id -> Specifying if sorting by timestamp along the CaseID is required


    Returns
    ------------
    mco
        SNA Matrix container object
    """
    if parameters is None:
        parameters = {}

    resource_key = parameters[
        constants.PARAMETER_CONSTANT_RESOURCE_KEY] if constants.PARAMETER_CONSTANT_RESOURCE_KEY in parameters else xes.DEFAULT_RESOURCE_KEY
    case_id_glue = parameters[
        constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else "case:concept:name"
    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    sort_caseid_required = parameters["sort_caseid_required"] if "sort_caseid_required" in parameters else True
    sort_timestamp_along_case_id = parameters[
        "sort_timestamp_along_case_id"] if "sort_timestamp_along_case_id" in parameters else True

    if sort_caseid_required:
        if sort_timestamp_along_case_id:
            df = df.sort_values([case_id_glue, timestamp_key])
        else:
            df = df.sort_values(case_id_glue)

    df_reduced = df[[case_id_glue, resource_key]]
    # shift the dataframe by 1, in order to couple successive rows
    df_reduced_shifted = df_reduced.shift(-1)
    # change column names to shifted dataframe
    df_reduced_shifted.columns = [str(col) + '_2' for col in df_reduced_shifted.columns]
    # concate the two dataframe to get a unique dataframe
    basic_df = pd.concat([df_reduced, df_reduced_shifted], axis=1)
    # as successive rows in the sorted dataframe may belong to different case IDs we have to restrict ourselves to
    # successive rows belonging to same case ID
    basic_df = basic_df[basic_df[case_id_glue] == basic_df[case_id_glue + '_2']]

    basic_df = \
        basic_df.rename(
            columns={resource_key: "resource", resource_key + '_2': "next_resource"})[
            ["resource", "next_resource"]]

    resources_set = df_utilities.get_resources_from_df(basic_df)

    mco = MatrixContainer(basic_df, resources_set)

    return mco
