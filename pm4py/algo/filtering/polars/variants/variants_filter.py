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
from pm4py.statistics.variants.polars import get as variants_get
from typing import Optional, Dict, Any, Union, List
import polars as pl


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    POSITIVE = "positive"


def apply(
    df: pl.LazyFrame,
    admitted_variants: List[List[str]],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Filter on variants

    Parameters
    -----------
    df
        LazyFrame
    admitted_variants
        List of variants to include/exclude
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

    # Convert admitted variants to strings
    variant_strings = [constants.DEFAULT_VARIANT_SEP.join(v) for v in admitted_variants]

    # Filter for matching variants
    matching_cases = variants_df.filter(
        pl.col("variant").is_in(variant_strings)
    ).select(case_id_glue)

    if positive:
        ret = df.join(matching_cases, on=case_id_glue, how="inner", maintain_order="left")
    else:
        ret = df.join(matching_cases, on=case_id_glue, how="anti", maintain_order="left")

    return ret


def filter_variants_top_k(
    log: pl.LazyFrame,
    k: int,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Keeps the top-k variants of the log

    Parameters
    -------------
    log
        Event log LazyFrame
    k
        Number of variants that should be kept
    parameters
        Parameters

    Returns
    -------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    variants = variants_get.get_variants_count(log, parameters=parameters)
    variant_count = []
    for variant, count in variants.items():
        variant_count.append([variant, count])
    variant_count = sorted(
        variant_count, key=lambda x: (x[1], x[0]), reverse=True
    )
    variant_count = variant_count[: min(k, len(variant_count))]
    variants_to_filter = [x[0] for x in variant_count]

    return apply(log, variants_to_filter, parameters=parameters)


def apply_auto_filter(
    df: pl.LazyFrame,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Apply auto filter on variants

    Parameters
    -----------
    df
        LazyFrame
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

    # Get variant counts
    variant_counts = (
        df.sort([case_id_glue, "time:timestamp"], maintain_order=True)
        .group_by(case_id_glue, maintain_order=True)
        .agg(
            pl.col(activity_key)
            .str.join(constants.DEFAULT_VARIANT_SEP)
            .alias("variant")
        )
        .group_by("variant")
        .len(name="count")
        .sort(["count", "variant"], descending=[True, True])
    )

    # Calculate cumulative percentage
    total_cases = variant_counts.select(pl.sum("count")).collect()[0, 0]
    variant_counts = variant_counts.with_columns(
        (pl.col("count").cum_sum() / total_cases).alias("cumulative_percentage")
    )

    # Keep variants covering 80% of cases
    selected_variants = (
        variant_counts
        .filter(pl.col("cumulative_percentage") <= 0.8)
        .select("variant")
        .collect()["variant"]
        .to_list()
    )

    # Apply filter
    return apply_from_variant_list(df, selected_variants, parameters)


def apply_from_variant_list(
    df: pl.LazyFrame,
    variants: List[str],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Apply filter from variant list

    Parameters
    -----------
    df
        LazyFrame
    variants
        List of variants (as strings)
    parameters
        Parameters

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

    # Filter for matching variants
    matching_cases = variants_df.filter(
        pl.col("variant").is_in(variants)
    ).select(case_id_glue)

    if positive:
        ret = df.join(matching_cases, on=case_id_glue, how="inner", maintain_order="left")
    else:
        ret = df.join(matching_cases, on=case_id_glue, how="anti", maintain_order="left")

    return ret
