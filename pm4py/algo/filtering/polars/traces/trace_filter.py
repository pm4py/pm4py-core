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
from pm4py.util.constants import CASE_CONCEPT_NAME, PARAMETER_CONSTANT_CASEID_KEY, PARAMETER_CONSTANT_ACTIVITY_KEY
from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants
from typing import Optional, Dict, Any, Union, List
import polars as pl
from pm4py.algo.filtering.common.traces.infix_to_regex import translate_infix_to_regex
import re


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
    Gets variants dataframe from a LazyFrame

    Parameters
    ----------
    df
        LazyFrame
    case_id_key
        Case ID key
    activity_key
        Activity key
    parameters
        Possible parameters of the algorithm

    Returns
    ----------
    variants_df
        Variants dataframe
    """
    if parameters is None:
        parameters = {}

    # Create variants by grouping activities per case
    variants_df = (
        df.sort([case_id_key, xes_constants.DEFAULT_TIMESTAMP_KEY], maintain_order=True)
        .group_by(case_id_key, maintain_order=True)
        .agg([
            pl.col(activity_key).alias("variant_list"),
            pl.len().alias("count")
        ])
        .with_columns(
            pl.col("variant_list").list.join(constants.DEFAULT_VARIANT_SEP).alias("variant")
        )
        .collect()
    )

    return variants_df


def apply(
    df: pl.LazyFrame,
    admitted_traces: List[List[str]],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Apply a filter on traces using regular expressions

    Parameters
    -----------
    df
        LazyFrame
    admitted_traces
        List of admitted traces (to include/exclude). Can contain "..." wildcard for any sequence of activities
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
        variants_df = get_variants_df(df, case_id_key=case_id_glue, activity_key=activity_key, parameters=parameters)

    # Build regex pattern from admitted traces
    filter_regex = "|".join(
        [f"({translate_infix_to_regex(inf)})" for inf in admitted_traces]
    )

    # Apply regex matching
    # Since Polars doesn't have a direct apply with lambda for regex, we need to use a different approach
    matching_cases = []
    for idx, row in enumerate(variants_df.iter_rows(named=True)):
        variant = row["variant"]
        if bool(re.search(filter_regex, variant)):
            matching_cases.append(row[case_id_glue])

    # Get the data type of the case ID column from the original dataframe
    case_id_dtype = df.select(pl.col(case_id_glue)).dtypes[0]

    # Create a DataFrame with matching cases
    if matching_cases:
        matching_df = pl.DataFrame({case_id_glue: matching_cases}).lazy()
    else:
        # Create empty DataFrame with the correct schema
        matching_df = pl.DataFrame({case_id_glue: []}, schema={case_id_glue: case_id_dtype}).lazy()

    # Filter based on positive/negative
    if positive:
        # Keep only matching cases
        ret = df.join(matching_df, on=case_id_glue, how="inner", maintain_order="left")
    else:
        # Keep only non-matching cases
        ret = df.join(matching_df, on=case_id_glue, how="anti", maintain_order="left")

    return ret