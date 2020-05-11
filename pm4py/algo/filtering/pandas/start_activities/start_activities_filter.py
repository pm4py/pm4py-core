from pm4py.algo.filtering.common import filtering_constants
from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.statistics.start_activities.common import get as start_activities_common
from pm4py.statistics.start_activities.pandas.get import get_start_activities
from pm4py.util import xes_constants as xes
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY
from pm4py.util.constants import GROUPED_DATAFRAME
from enum import Enum
from pm4py.util import exec_utils


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    DECREASING_FACTOR = "decreasingFactor"
    GROUP_DATAFRAME = GROUPED_DATAFRAME
    POSITIVE = "positive"


def apply(df, values, parameters=None):
    """
    Filter dataframe on start activities

    Parameters
    ----------
    df
        Dataframe
    values
        Values to filter on
    parameters
        Possible parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Case ID column in the dataframe
            Parameters.ACTIVITY_KEY -> Column that represents the activity
            Parameters.POSITIVE -> Specifies if the filtered should be applied including traces (positive=True)
            or excluding traces (positive=False)

    Returns
    ----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)
    grouped_df = exec_utils.get_param_value(Parameters.GROUP_DATAFRAME, parameters, None)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    return filter_df_on_start_activities(df, values, case_id_glue=case_id_glue, activity_key=activity_key,
                                         positive=positive, grouped_df=grouped_df)


def apply_auto_filter(df, parameters=None):
    """
    Apply auto filter on end activities

    Parameters
    -----------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Case ID column in the dataframe
            Parameters.ACTIVITY_KEY -> Column that represents the activity
            Parameters.DECREASING_FACTOR -> Decreasing factor that should be passed to the algorithm

    Returns
    -----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)
    grouped_df = exec_utils.get_param_value(Parameters.GROUP_DATAFRAME, parameters, None)
    decreasing_factor = exec_utils.get_param_value(Parameters.DECREASING_FACTOR, parameters,
                                                   filtering_constants.DECREASING_FACTOR)

    start_activities = get_start_activities(df, parameters=parameters)
    salist = start_activities_common.get_sorted_start_activities_list(start_activities)
    sathreshold = start_activities_common.get_start_activities_threshold(salist, decreasing_factor)

    return filter_df_on_start_activities_nocc(df, sathreshold, sa_count0=start_activities, case_id_glue=case_id_glue,
                                              activity_key=activity_key, grouped_df=grouped_df)


def filter_df_on_start_activities(df, values, case_id_glue=CASE_CONCEPT_NAME,
                                  activity_key=xes.DEFAULT_NAME_KEY, grouped_df=None, positive=True):
    """
    Filter dataframe on start activities

    Parameters
    ----------
    df
        Dataframe
    values
        Values to filter on
    case_id_glue
        Case ID column in the dataframe
    activity_key
        Column that represent the activity
    grouped_df
        Grouped dataframe
    positive
        Specifies if the filtered should be applied including traces (positive=True) or excluding traces
        (positive=False)

    Returns
    ----------
    df
        Filtered dataframe
    """

    if grouped_df is None:
        grouped_df = df.groupby(case_id_glue)
    first_eve_df = grouped_df.first()
    first_eve_df = first_eve_df[first_eve_df[activity_key].isin(values)]
    i1 = df.set_index(case_id_glue).index
    i2 = first_eve_df.index
    if positive:
        return df[i1.isin(i2)]
    return df[~i1.isin(i2)]


def filter_df_on_start_activities_nocc(df, nocc, sa_count0=None, case_id_glue=CASE_CONCEPT_NAME,
                                       activity_key=DEFAULT_NAME_KEY, grouped_df=None):
    """
    Filter dataframe on start activities number of occurrences

    Parameters
    -----------
    df
        Dataframe
    nocc
        Minimum number of occurrences of the start activity
    sa_count0
        (if provided) Dictionary that associates each start activity with its count
    case_id_glue
        Column that contains the Case ID
    activity_key
        Column that contains the activity
    grouped_df
        Grouped dataframe

    Returns
    ------------
    df
        Filtered dataframe
    """
    if grouped_df is None:
        grouped_df = df.groupby(case_id_glue)
    first_eve_df = grouped_df.first()
    if sa_count0 is None:
        parameters = {
            Parameters.CASE_ID_KEY: case_id_glue,
            Parameters.ACTIVITY_KEY: activity_key,
            Parameters.GROUP_DATAFRAME: grouped_df
        }
        sa_count0 = get_start_activities(df, parameters=parameters)
    sa_count = [k for k, v in sa_count0.items() if v >= nocc]
    if len(sa_count) < len(sa_count0):
        first_eve_df = first_eve_df[first_eve_df[activity_key].isin(sa_count)]
        i1 = df.set_index(case_id_glue).index
        i2 = first_eve_df.index
        return df[i1.isin(i2)]
    return df
