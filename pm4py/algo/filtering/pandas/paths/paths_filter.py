import pandas as pd

from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY
from enum import Enum
from pm4py.util import exec_utils


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ATTRIBUTE_KEY = PARAMETER_CONSTANT_ATTRIBUTE_KEY
    TIMESTAMP_KEY = PARAMETER_CONSTANT_TIMESTAMP_KEY
    DECREASING_FACTOR = "decreasingFactor"
    POSITIVE = "positive"


def apply(df, paths, parameters=None):
    """
    Apply a filter on traces containing / not containing a path

    Parameters
    ----------
    df
        Dataframe
    paths
        Paths to filter on
    parameters
        Possible parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Case ID column in the dataframe
            Parameters.ATTRIBUTE_KEY -> Attribute we want to filter
            Parameters.POSITIVE -> Specifies if the filter should be applied including traces (positive=True)
            or excluding traces (positive=False)
    Returns
    ----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}
    paths = [path[0] + "," + path[1] for path in paths]
    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)
    df = df.sort_values([case_id_glue, timestamp_key])
    filt_df = df[[case_id_glue, attribute_key]]
    filt_dif_shifted = filt_df.shift(-1)
    filt_dif_shifted.columns = [str(col) + '_2' for col in filt_dif_shifted.columns]
    stacked_df = pd.concat([filt_df, filt_dif_shifted], axis=1)
    stacked_df["@@path"] = stacked_df[attribute_key] + "," + stacked_df[attribute_key + "_2"]
    stacked_df = stacked_df[stacked_df["@@path"].isin(paths)]
    i1 = df.set_index(case_id_glue).index
    i2 = stacked_df.set_index(case_id_glue).index
    if positive:
        return df[i1.isin(i2)]
    else:
        return df[~i1.isin(i2)]


def apply_auto_filter(df, parameters=None):
    del df
    del parameters
    raise Exception("apply_auto_filter method not available for paths filter on dataframe")
