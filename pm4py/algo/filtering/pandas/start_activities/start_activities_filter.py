from pm4py.algo.filtering.common import filtering_constants
from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME
from pm4py.algo.filtering.common.start_activities import start_activities_common
from pm4py.objects.log.util import xes
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY


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
    positive = parameters["positive"] if "positive" in parameters else True

    return filter_df_on_start_activities(df, values, case_id_glue=case_id_glue, activity_key=activity_key,
                                         positive=positive)


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

    start_activities = get_start_activities(df, parameters=parameters)
    salist = start_activities_common.get_sorted_start_activities_list(start_activities)
    sathreshold = start_activities_common.get_start_activities_threshold(salist, decreasing_factor)

    return filter_df_on_start_activities_nocc(df, sathreshold, sa_count=start_activities, case_id_glue=case_id_glue,
                                              activity_key=activity_key)


def get_start_activities(df, parameters=None):
    """
    Get start activities count

    Parameters
    -----------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
            case_id_glue -> Case ID column in the dataframe
            activity_key -> Column that represents the activity

    Returns
    -----------
    startact_dict
        Dictionary of start activities along with their count
    """
    if parameters is None:
        parameters = {}

    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY

    first_eve_df = df.groupby(case_id_glue).first()
    startact_dict = dict(first_eve_df[activity_key].value_counts())
    return startact_dict


def filter_df_on_start_activities(df, values, case_id_glue=filtering_constants.CASE_CONCEPT_NAME,
                                  activity_key=xes.DEFAULT_NAME_KEY, positive=True):
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
    positive
        Specifies if the filtered should be applied including traces (positive=True) or excluding traces
        (positive=False)

    Returns
    ----------
    df
        Filtered dataframe
    """
    first_eve_df = df.groupby(case_id_glue).first()
    first_eve_df = first_eve_df[first_eve_df[activity_key].isin(values)]
    i1 = df.set_index(case_id_glue).index
    i2 = first_eve_df.index
    if positive:
        return df[i1.isin(i2)]
    return df[~i1.isin(i2)]


def filter_df_on_start_activities_nocc(df, nocc, sa_count=None, case_id_glue=CASE_CONCEPT_NAME,
                                       activity_key=DEFAULT_NAME_KEY):
    """
    Filter dataframe on start activities number of occurrences

    Parameters
    -----------
    df
        Dataframe
    nocc
        Minimum number of occurrences of the start activity
    sa_count
        (if provided) Dictionary that associates each start activity with its count
    case_id_glue
        Column that contains the Case ID
    activity_key
        Column that contains the activity

    Returns
    ------------
    df
        Filtered dataframe
    """
    first_eve_df = df.groupby(case_id_glue).first()
    if sa_count is None:
        sa_count = get_start_activities(df)
    sa_count = [k for k, v in sa_count.items() if v >= nocc]
    first_eve_df = first_eve_df[first_eve_df[activity_key].isin(sa_count)]
    i1 = df.set_index(case_id_glue).index
    i2 = first_eve_df.index
    return df[i1.isin(i2)]
