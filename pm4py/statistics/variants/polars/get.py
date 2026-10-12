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
from typing import Optional, Dict, Any, Union, List, Set, Tuple, Collection
import polars as pl
from collections import Counter
from pm4py.util import constants, xes_constants, exec_utils
from enum import Enum


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


def pandas_numpy_variants_apply_polars(
    lf: pl.LazyFrame, parameters=None
) -> Tuple[Dict[Tuple[str, ...], int], Dict[str, Tuple[str, ...]]]:
    """
    Efficient method returning the variants from a Polars LazyFrame

    Parameters
    ------------------
    lf
        LazyFrame
    parameters
        Parameters of the algorithm, including:
        - Parameters.CASE_ID_KEY => the case identifier
        - Parameters.ACTIVITY_KEY => the activity
        - Parameters.TIMESTAMP_KEY => the timestamp

    Returns
    ------------------
    variants_dict
        Dictionary associating to each variant the number of occurrences in the dataframe
    case_variant
        Dictionary associating to each case identifier the corresponding variant
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME
    )
    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
    )
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY,
        parameters,
        xes_constants.DEFAULT_TIMESTAMP_KEY,
    )

    # Sort by case and timestamp to ensure proper order
    sorted_lf = lf.sort([case_id_key, timestamp_key], maintain_order=True)

    # Group by case and collect activities as lists
    # In Polars, aggregating without specifying a function collects into lists by default
    case_variants_df = (
        sorted_lf.group_by(case_id_key, maintain_order=True)
        .agg(pl.col(activity_key))
        .collect()
    )

    case_variant = {}
    variants_counter = Counter()

    for row in case_variants_df.iter_rows():
        case_id = row[0]
        activities = tuple(row[1])  # Convert list to tuple
        case_variant[case_id] = activities
        variants_counter[activities] += 1

    # Return as Python dictionaries
    variants_dict = {x: y for x, y in variants_counter.items()}

    return variants_dict, case_variant


def get_variants_count(
    lf: pl.LazyFrame, parameters: Optional[Dict[Any, Any]] = None
) -> Dict[Tuple[str, ...], int]:
    """
    Gets the dictionary of variants from the current LazyFrame

    Parameters
    --------------
    lf
        LazyFrame
    parameters
        Possible parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Column that contains the activity

    Returns
    --------------
    variants_dict
        Dictionary of variants in the log
    """
    if parameters is None:
        parameters = {}

    variants_counter, case_variant = pandas_numpy_variants_apply_polars(
        lf, parameters=parameters
    )

    return variants_counter


def get_variants_set(
    lf: pl.LazyFrame, parameters: Optional[Dict[Any, Any]] = None
) -> Set[Tuple[str, ...]]:
    """
    Gets the set of variants from the current LazyFrame

    Parameters
    --------------
    lf
        LazyFrame
    parameters
        Possible parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Column that contains the activity

    Returns
    --------------
    variants_set
        Set of variants in the log
    """
    if parameters is None:
        parameters = {}

    variants_dict = get_variants_count(lf, parameters=parameters)

    return set(variants_dict.keys())