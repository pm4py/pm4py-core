'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''
from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.util.constants import (
    PARAMETER_CONSTANT_CASEID_KEY,
    PARAMETER_CONSTANT_ACTIVITY_KEY,
)
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, List
import polars as pl
from pm4py.util import constants, xes_constants


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    DECREASING_FACTOR = "decreasingFactor"
    POSITIVE = "positive"


def get_variants_df(
    df: pl.LazyFrame,
    case_id_key: str = CASE_CONCEPT_NAME,
    activity_key: str = xes_constants.DEFAULT_NAME_KEY,
    parameters: Optional[Dict[Any, Any]] = None,
) -> pl.DataFrame:
    """
    Get variants dataframe from a LazyFrame

    Parameters
    ----------
    df
        LazyFrame
    case_id_key
        Case ID column
    activity_key
        Activity column
    parameters
        Parameters

    Returns
    ----------
    variants_df
        DataFrame with variants
    """
    if parameters is None:
        parameters = {}

    # Create variants by concatenating activities per case
    variants_df = (
        df.sort([case_id_key, "time:timestamp"], maintain_order=True)  # Ensure events are ordered
        .group_by(case_id_key, maintain_order=True)
        .agg(
            pl.col(activity_key)
            .str.join(constants.DEFAULT_VARIANT_SEP)
            .alias("variant")
        )
        .collect()
    )

    return variants_df


def apply(
    df: pl.LazyFrame,
    admitted_suffixes: List[str],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Apply a filter on variants

    Parameters
    -----------
    df
        LazyFrame
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
    positive = exec_utils.get_param_value(
        Parameters.POSITIVE, parameters, True
    )

    # Get or calculate variants dataframe
    variants_df = parameters.get("variants_df")
    if variants_df is None:
        variants_df = get_variants_df(df, case_id_glue, activity_key, parameters)

    # Handle suffix formats
    admitted_suffixes = list(admitted_suffixes)
    if isinstance(admitted_suffixes[0], (list, tuple)):
        # Convert list/tuple suffixes to string format
        admitted_suffixes = [
            constants.DEFAULT_VARIANT_SEP.join(x) for x in admitted_suffixes
        ]

    # Filter variants that end with admitted suffixes
    suffix_expr = None
    for suffix in admitted_suffixes:
        if suffix_expr is None:
            suffix_expr = pl.col("variant").str.ends_with(suffix)
        else:
            suffix_expr = suffix_expr | pl.col("variant").str.ends_with(suffix)

    matching_cases = variants_df.filter(suffix_expr).select(case_id_glue)

    if positive:
        # Keep cases with matching suffixes
        ret = df.join(matching_cases.lazy(), on=case_id_glue, how="inner", maintain_order="left")
    else:
        # Keep cases without matching suffixes
        ret = df.join(matching_cases.lazy(), on=case_id_glue, how="anti", maintain_order="left")

    return ret