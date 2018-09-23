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

    Returns
    ------------
    df
        Filtered dataframe
    """

    # list of filters that are applied:
    # - activities
    # - variants filter
    # - end activities filter
    # - start activities filter
    df = attributes_filter.apply_auto_filter(df, parameters=parameters)
    df = variants_filter.apply_auto_filter(df, parameters=parameters)
    df = end_activities_filter.apply_auto_filter(df, parameters=parameters)
    df = start_activities_filter.apply_auto_filter(df, parameters=parameters)

    return df