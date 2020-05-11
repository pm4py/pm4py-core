from pm4py.algo.filtering.pandas.attributes import attributes_filter
from pm4py.algo.filtering.pandas.end_activities import end_activities_filter
from pm4py.algo.filtering.pandas.start_activities import start_activities_filter
from pm4py.algo.filtering.pandas.variants import variants_filter
from pm4py.util import constants
from enum import Enum
from pm4py.util import exec_utils


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    DECREASING_FACTOR = "decreasingFactor"
    POSITIVE = "positive"
    RETURN_EA_COUNT = constants.RETURN_EA_COUNT_DICT_AUTOFILTER
    ENABLE_ACTIVITES_FILTER = "enable_activities_filter"
    ENABLE_VARIANTS_FILTER = "enable_variants_filter"
    ENABLE_START_ACTIVITIES_FILTER = "enable_start_activities_filter"
    ENABLE_END_ACTIVITIES_FILTER = "enable_end_activities_filter"


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
            Parameters.CASE_ID_KEY -> Column where the case ID is present
            Parameters.ACTIVITY_KEY -> Column where the activity is present
            Parameters.DECREASING_FACTOR -> Decreasing factor (provided to all algorithms)
            Parameters.ENABLE_ACTIVITES_FILTER -> Enables or disables auto filter on activities number
            (it is useful to disable if the dataframe has been already filtered by activities number before).
            Default is True
            Parameters.ENABLE_VARIANTS_FILTER -> Enables or disables auto filter on variants (that is slower than others).
            Default is False
            Parameters.ENABLE_START_ACTIVITIES_FILTER -> Enables or disables auto filter on start activities. Default is False
            Parameters.ENABLE_END_ACTIVITIES_FILTER -> Enables or disables auto filter on end activities. Default is True

    Returns
    ------------
    df
        Filtered dataframe
    """

    if parameters is None:
        parameters = {}

    enable_activities_filter = exec_utils.get_param_value(Parameters.ENABLE_ACTIVITES_FILTER, parameters, True)
    enable_variants_filter = exec_utils.get_param_value(Parameters.ENABLE_VARIANTS_FILTER, parameters, False)
    enable_start_activities_filter = exec_utils.get_param_value(Parameters.ENABLE_START_ACTIVITIES_FILTER, parameters,
                                                                False)
    enable_end_activities_filter = exec_utils.get_param_value(Parameters.ENABLE_END_ACTIVITIES_FILTER, parameters, True)
    return_dict = exec_utils.get_param_value(Parameters.RETURN_EA_COUNT, parameters, False)

    ea_dict = None

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
        parameters[constants.RETURN_EA_COUNT_DICT_AUTOFILTER] = return_dict
        if return_dict:
            df, ea_dict = end_activities_filter.apply_auto_filter(df, parameters=parameters)
        else:
            df = end_activities_filter.apply_auto_filter(df, parameters=parameters)
    if enable_start_activities_filter:
        df = start_activities_filter.apply_auto_filter(df, parameters=parameters)

    if return_dict:
        return df, ea_dict

    return df
