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
import sys
from enum import Enum
from typing import Any, Optional, Dict, Union

import polars as pl

from pm4py.util import constants, xes_constants, exec_utils


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    MIN_REP = "min_rep"
    MAX_REP = "max_rep"


def apply(
    df: pl.LazyFrame,
    value: Any,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Filters the trace of the LazyFrame where the given attribute value is repeated
    (in a range of repetitions that is specified by the user)

    Parameters
    ----------------
    df
        LazyFrame
    value
        Value that is investigated
    parameters
        Parameters of the filter, including:
        - Parameters.ATTRIBUTE_KEY => the attribute key
        - Parameters.MIN_REP => minimum number of repetitions
        - Parameters.MAX_REP => maximum number of repetitions
        - Parameters.CASE_ID_KEY => the columns of the LazyFrame that is the case identifier

    Returns
    ----------------
    filtered_df
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME
    )
    attribute_key = exec_utils.get_param_value(
        Parameters.ATTRIBUTE_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
    )
    min_rep = exec_utils.get_param_value(Parameters.MIN_REP, parameters, 2)
    max_rep = exec_utils.get_param_value(
        Parameters.MAX_REP, parameters, sys.maxsize
    )

    # Filter events with the specified value
    filtered_df = df.filter(pl.col(attribute_key) == value)

    # Count occurrences per case
    case_counts = (
        filtered_df
        .group_by(case_id_key)
        .len(name="count")
        .filter(
            (pl.col("count") >= min_rep) & (pl.col("count") <= max_rep)
        )
        .select(case_id_key)
    )

    # Keep only cases that meet the repetition criteria
    ret = df.join(case_counts, on=case_id_key, how="inner", maintain_order="left")

    return ret