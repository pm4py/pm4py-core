from pm4py.entities.log.util import xes
from pm4py.util import constants
from pm4py.algo.filtering.common import filtering_constants
from pm4py.algo.cases.pandas import case_statistics
import time

def apply_auto_filter(df, parameters=None):
    """
    Apply an automatic filter on variants

    Parameters
    -----------
    df
        Dataframe
    admitted_variants
        List of admitted variants (to include/exclude)
    parameters
        Parameters of the algorithm, including:
            case_id_glue -> Column that contains the Case ID
            activity_key -> Column that contains the activity
            variants_df -> If provided, avoid recalculation of the variants dataframe
            decreasingFactor -> Decreasing factor that should be passed to the algorithm

    Returns
    -----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}
    case_id_glue = parameters[constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else filtering_constants.CASE_CONCEPT_NAME
    variants_df = case_statistics.get_variants_df(df, parameters=parameters)
    parameters["variants_df"] = variants_df
    variants = case_statistics.get_variants_statistics(df, parameters=parameters)
    decreasingFactor = parameters["decreasingFactor"] if "decreasingFactor" in parameters else filtering_constants.DECREASING_FACTOR

    admitted_variants = []
    if len(variants) > 0:
        currentVariantCount = variants[0][case_id_glue]

        i = 0
        while i < len(variants):
            if variants[i][case_id_glue] >= decreasingFactor * currentVariantCount:
                admitted_variants.append(variants[i]["variant"])
            else:
                break
            currentVariantCount = variants[i][case_id_glue]
            i = i + 1

    return apply(df, admitted_variants, parameters=parameters)

def apply(df, admitted_variants, parameters=None):
    """
    Apply a filter on variants

    Parameters
    -----------
    df
        Dataframe
    admitted_variants
        List of admitted variants (to include/exclude)
    parameters
        Parameters of the algorithm, including:
            case_id_glue -> Column that contains the Case ID
            activity_key -> Column that contains the activity
            positive -> Specifies if the filter should be applied including traces (positive=True) or excluding traces (positive=False)
            variants_df -> If provided, avoid recalculation of the variants dataframe

    Returns
    -----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = parameters[constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else filtering_constants.CASE_CONCEPT_NAME
    positive = parameters["positive"] if "positive" in parameters else True
    variants_df = parameters["variants_df"] if "variants_df" in parameters else case_statistics.get_variants_df(df, parameters=parameters)
    variants_df = variants_df[variants_df["variant"].isin(admitted_variants)]
    i1 = df.set_index(case_id_glue).index
    i2 = variants_df.index
    if positive:
        ret = df[i1.isin(i2)]
    else:
        ret = df[~i1.isin(i2)]
    return ret