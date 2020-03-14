from pm4py.algo.filtering.common import filtering_constants
from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.statistics.start_activities.common import get as start_activities_common
from pm4py.statistics.start_activities.pandas.get import get_start_activities
from pm4py.util import xes_constants as xes
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY
from pm4py.util.constants import GROUPED_DATAFRAME



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
            case_id_glue -> Case ID column in the dataframe
            activity_key -> Column that represents the activity
            positive -> Specifies if the filtered should be applied including traces (positive=True)
            or excluding traces (positive=False)

    Returns
    ----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}
    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY
    grouped_df = parameters[GROUPED_DATAFRAME] if GROUPED_DATAFRAME in parameters else None
    positive = parameters["positive"] if "positive" in parameters else True

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
            case_id_glue -> Case ID column in the dataframe
            activity_key -> Column that represents the activity
            decreasingFactor -> Decreasing factor that should be passed to the algorithm

    Returns
    -----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY
    decreasing_factor = parameters[
        "decreasingFactor"] if "decreasingFactor" in parameters else filtering_constants.DECREASING_FACTOR
    grouped_df = parameters[GROUPED_DATAFRAME] if GROUPED_DATAFRAME in parameters else None

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
            PARAMETER_CONSTANT_CASEID_KEY: case_id_glue,
            PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key,
            GROUPED_DATAFRAME: grouped_df
        }
        sa_count0 = get_start_activities(df, parameters=parameters)
    sa_count = [k for k, v in sa_count0.items() if v >= nocc]
    if len(sa_count) < len(sa_count0):
        first_eve_df = first_eve_df[first_eve_df[activity_key].isin(sa_count)]
        i1 = df.set_index(case_id_glue).index
        i2 = first_eve_df.index
        return df[i1.isin(i2)]
    return df
