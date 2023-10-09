from pm4py.algo.filtering.common import filtering_constants
from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.statistics.traces.generic.pandas import case_statistics
from pm4py.statistics.traces.generic.pandas.case_statistics import get_variants_df
from pm4py.statistics.variants.pandas import get as variants_get
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY, PARAMETER_CONSTANT_ACTIVITY_KEY
from enum import Enum
from pm4py.util import exec_utils
from copy import copy
from typing import Optional, Dict, Any, Union, Tuple, List
import pandas as pd
from pm4py.util import variants_util, constants


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    DECREASING_FACTOR = "decreasingFactor"
    POSITIVE = "positive"


def apply(df: pd.DataFrame, admitted_suffixes: List[str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> pd.DataFrame:
    """
    Apply a filter on variants

    Parameters
    -----------
    df
        Dataframe
    admitted_suffixes
        List of admitted suffixes (to include/exclude)
    parameters
        Parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Column that contains the Case ID
            Parameters.ACTIVITY_KEY -> Column that contains the activity
            Parameters.POSITIVE -> Specifies if the filter should be applied including traces (positive=True)
            or excluding traces (positive=False)
            variants_df -> If provided, avoid recalculation of the variants dataframe

    Returns
    -----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)
    variants_df = parameters["variants_df"] if "variants_df" in parameters else get_variants_df(df,
                                                                                                parameters=parameters)

    admitted_suffixes = list(admitted_suffixes)
    first_case_variant = variants_df["variant"].iloc[0]
    if isinstance(first_case_variant, tuple):
        # manage that as tuple
        variants_df = variants_df.copy()
        variants_df["variant"] = variants_df["variant"].apply(lambda x: constants.DEFAULT_VARIANT_SEP.join(list(x)))
        admitted_suffixes = [constants.DEFAULT_VARIANT_SEP.join(x) for x in admitted_suffixes]
    admitted_suffixes = tuple(admitted_suffixes)

    variants_df = variants_df[variants_df["variant"].str.endswith(admitted_suffixes)]

    i1 = df.set_index(case_id_glue).index
    i2 = variants_df.index
    if positive:
        ret = df[i1.isin(i2)]
    else:
        ret = df[~i1.isin(i2)]

    ret.attrs = copy(df.attrs) if hasattr(df, 'attrs') else {}
    return ret
