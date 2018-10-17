from pm4py.algo.filtering.pandas.attributes import attributes_filter
from pm4py.algo.filtering.pandas.end_activities import end_activities_filter
from pm4py.algo.filtering.pandas.start_activities import start_activities_filter
from pm4py.algo.filtering.pandas.variants import variants_filter


def apply_auto_filter(df, parameters=None):
    """
    Apply some filters to Pandas dataframe in order to get
    a simpler dataframe

    Parameters
    ------------
    df
        Dataframe
    parameters
        Eventual parameters passed to the algorithms:
            case_id_glue -> Column where the case ID is present
            activity_key -> Column where the activity is present
            decreasingFactor -> Decreasing factor (provided to all algorithms)
            enable_activities_filter -> Enables or disables auto filter on activities number
            (it is useful to disable if the dataframe has been already filtered by activities number before).
            Default is True
            enable_variants_filter -> Enables or disables auto filter on variants (that is slower than others).
            Default is False
            enable_start_activities_filter -> Enables or disables auto filter on start activities. Default is False
            enable_end_activities_filter -> Enables or disables auto filter on end activities. Default is True

    Returns
    ------------
    df
        Filtered dataframe
    """

    if parameters is None:
        parameters = {}

    enable_activities_filter = parameters[
        "enable_activities_filter"] if "enable_activities_filter" in parameters else True
    enable_variants_filter = parameters["enable_variants_filter"] if "enable_variants_filter" in parameters else False
    enable_start_activities_filter = parameters[
        "enable_start_activities_filter"] if "enable_start_activities_filter" in parameters else False
    enable_end_activities_filter = parameters[
        "enable_end_activities_filter"] if "enable_end_activities_filter" in parameters else True

    # list of filters that are applied:
    # - activities (if enabled)
    # - variants filter (if enabled)
    # - end activities filter (if enabled)
    # - start activities filter (if enabled)
    if enable_activities_filter:
        df = attributes_filter.apply_auto_filter(df, parameters=parameters)
    if enable_variants_filter:
        df = variants_filter.apply_auto_filter(df, parameters=parameters)
    if enable_end_activities_filter:
        df = end_activities_filter.apply_auto_filter(df, parameters=parameters)
    if enable_start_activities_filter:
        df = start_activities_filter.apply_auto_filter(df, parameters=parameters)

    return df
