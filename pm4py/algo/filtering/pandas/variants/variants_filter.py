from pm4py.algo.filtering.common import filtering_constants
from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME
from pm4py.statistics.traces.pandas import case_statistics
from pm4py.statistics.traces.pandas.case_statistics import get_variants_df
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY


def apply_auto_filter(df, parameters=None):
    """
    Apply an automatic filter on variants

    Parameters
    -----------
    df
        Dataframe
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
    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    variants_df = case_statistics.get_variants_df(df, parameters=parameters)
    parameters["variants_df"] = variants_df
    variants = case_statistics.get_variant_statistics(df, parameters=parameters)
    decreasing_factor = parameters[
        "decreasingFactor"] if "decreasingFactor" in parameters else filtering_constants.DECREASING_FACTOR

    admitted_variants = []
    if len(variants) > 0:
        current_variant_count = variants[0][case_id_glue]

        for i in range(len(variants)):
            if variants[i][case_id_glue] >= decreasing_factor * current_variant_count:
                admitted_variants.append(variants[i]["variant"])
            else:
                break
            current_variant_count = variants[i][case_id_glue]

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
            positive -> Specifies if the filter should be applied including traces (positive=True)
            or excluding traces (positive=False)
            variants_df -> If provided, avoid recalculation of the variants dataframe

    Returns
    -----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    positive = parameters["positive"] if "positive" in parameters else True
    variants_df = parameters["variants_df"] if "variants_df" in parameters else get_variants_df(df,
                                                                                                parameters=parameters)
    variants_df = variants_df[variants_df["variant"].isin(admitted_variants)]
    i1 = df.set_index(case_id_glue).index
    i2 = variants_df.index
    if positive:
        ret = df[i1.isin(i2)]
    else:
        ret = df[~i1.isin(i2)]
    return ret
