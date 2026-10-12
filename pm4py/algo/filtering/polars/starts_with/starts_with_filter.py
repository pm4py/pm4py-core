from pm4py.util.constants import CASE_CONCEPT_NAME, PARAMETER_CONSTANT_CASEID_KEY, PARAMETER_CONSTANT_ACTIVITY_KEY
from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants
from typing import Optional, Dict, Any, Union, List
import polars as pl


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    POSITIVE = "positive"


def apply(
    df: pl.LazyFrame,
    prefixes: List[List[str]],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Filter cases that start with a given prefix

    Parameters
    -----------
    df
        LazyFrame
    prefixes
        List of prefixes to match
    parameters
        Parameters of the algorithm

    Returns
    -----------
    df
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME
    )
    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
    )
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    # Create variants
    variants_df = (
        df.sort([case_id_glue, "time:timestamp"], maintain_order=True)
        .group_by(case_id_glue, maintain_order=True)
        .agg(
            pl.col(activity_key)
            .str.join(constants.DEFAULT_VARIANT_SEP)
            .alias("variant")
        )
    )

    # Convert prefixes to strings
    prefix_strings = [constants.DEFAULT_VARIANT_SEP.join(p) for p in prefixes]

    # Check if variant starts with any prefix
    prefix_expr = None
    for prefix in prefix_strings:
        if prefix_expr is None:
            prefix_expr = pl.col("variant").str.starts_with(prefix)
        else:
            prefix_expr = prefix_expr | pl.col("variant").str.starts_with(prefix)

    matching_cases = variants_df.filter(prefix_expr).select(case_id_glue)

    if positive:
        ret = df.join(matching_cases, on=case_id_glue, how="inner", maintain_order="left")
    else:
        ret = df.join(matching_cases, on=case_id_glue, how="anti", maintain_order="left")

    return ret
