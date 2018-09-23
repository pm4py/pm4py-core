from pm4py.entities.log.util import xes
from pm4py.util import constants
from pm4py.algo.filtering.common import filtering_constants

def get_variants(df, parameters=None):
    """
    Get variants from a Pandas dataframe

    Parameters
    -----------
    df
        Dataframe
    parameters
        Parameters of the algorithm, including:
            case_id_glue -> Column that contains the Case ID
            activity_key -> Column that contains the activity
            max_variants_to_return -> Maximum number of variants to return

    Returns
    -----------
    variants_list
        List of variants inside the Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = parameters[constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else filtering_constants.CASE_CONCEPT_NAME
    activity_key = parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    max_variants_to_return = parameters["max_variants_to_return"] if "max_variants_to_return" in parameters else None
    variantsDf = df.groupby(case_id_glue)[activity_key].agg({'variant': lambda col: ','.join(col)}).reset_index()
    variantsList = variantsDf.groupby("variant").agg("count").reset_index().to_dict('records')
    variantsList = sorted(variantsList, key=lambda x: x[case_id_glue], reverse=True)
    if max_variants_to_return:
        variantsList = variantsList[:min(len(variantsList), max_variants_to_return)]
    return variantsList

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

    Returns
    -----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = parameters[constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else filtering_constants.CASE_CONCEPT_NAME
    activity_key = parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    positive = parameters["positive"] if "positive" in parameters else True

    variantsDf = df.groupby(case_id_glue)[activity_key].agg({'variant': lambda col: ','.join(col)})
    variantsDf = variantsDf[variantsDf["variant"].isin(admitted_variants)]
    i1 = df.set_index(case_id_glue).index
    i2 = variantsDf.index

    if positive:
        return df[i1.isin(i2)]

    return df[~i1.isin(i2)]