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
from typing import Optional, Dict, Any, Union, Set
import polars as pl


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    MIN_OCCURRENCES = "min_occurrences"


def apply(
    df: pl.LazyFrame,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Filters the cases where the specified activity occurs at least min_occurrences times.

    Parameters
    -----------
    df
        LazyFrame
    parameters
        Parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Column that contains the Case ID
            Parameters.ACTIVITY_KEY -> Column that contains the activity
            Parameters.MIN_OCCURRENCES -> Minimum occurrences of the activity (default: 2)

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
    min_occurrences = exec_utils.get_param_value(
        Parameters.MIN_OCCURRENCES, parameters, 2
    )

    # Count occurrences of each activity per case
    activity_counts = (
        df.group_by([case_id_glue, activity_key])
        .len(name="count")
        .filter(pl.col("count") >= min_occurrences)
        .select(case_id_glue)
        .unique()
    )

    # Keep only cases with rework
    ret = df.join(activity_counts, on=case_id_glue, how="inner", maintain_order="left")

    return ret


def apply_activity_set(
    df: pl.LazyFrame,
    activities: Set[str],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Filters the cases where at least one of the specified activities occurs at least min_occurrences times.

    Parameters
    -----------
    df
        LazyFrame
    activities
        Set of activities to check for rework
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
    min_occurrences = exec_utils.get_param_value(
        Parameters.MIN_OCCURRENCES, parameters, 2
    )

    # Filter for specified activities and count occurrences
    activity_counts = (
        df.filter(pl.col(activity_key).is_in(list(activities)))
        .group_by([case_id_glue, activity_key])
        .len(name="count")
        .filter(pl.col("count") >= min_occurrences)
        .select(case_id_glue)
        .unique()
    )

    # Keep only cases with rework
    ret = df.join(activity_counts, on=case_id_glue, how="inner", maintain_order="left")

    return ret
