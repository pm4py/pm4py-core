from pm4py.entities.log.util import xes
from pm4py.util import constants
import pandas as pd
from pm4py.algo.filtering.common import filtering_constants

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
            case_id_glue -> Case ID column in the dataframe
            attribute_key -> Attribute we want to filter
            positive -> Specifies if the filter should be applied including traces (positive=True) or excluding traces (positive=False)
    Returns
    ----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}
    paths = [path[0]+","+path[1] for path in paths]
    case_id_glue = parameters[constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else filtering_constants.CASE_CONCEPT_NAME
    attribute_key = parameters[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] if constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else xes.DEFAULT_NAME_KEY
    positive = parameters["positive"] if "positive" in parameters else True
    filtDf = df[[case_id_glue, attribute_key]]
    filtDifShifted = filtDf.shift(-1)
    filtDifShifted.columns = [str(col) + '_2' for col in filtDifShifted.columns]
    stackedDf = pd.concat([filtDf, filtDifShifted], axis=1)
    stackedDf["@@path"] = stackedDf[attribute_key] + "," + stackedDf[attribute_key+"_2"]
    stackedDf = stackedDf[stackedDf["@@path"].isin(paths)]
    i1 = df.set_index(case_id_glue).index
    i2 = stackedDf.set_index(case_id_glue).index
    if positive:
        return df[i1.isin(i2)]
    else:
        return df[~i1.isin(i2)]

def apply_auto_filter(df, parameters=None):
    raise Exception("apply_auto_filter method not available for paths filter on dataframe")