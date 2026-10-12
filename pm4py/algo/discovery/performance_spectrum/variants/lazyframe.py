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

from enum import Enum
from typing import Any, Dict, List, Optional, Union

import polars as pl

from pm4py.util import constants
from pm4py.util import exec_utils
from pm4py.util import xes_constants as xes
from pm4py.util.constants import CASE_CONCEPT_NAME


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    PARAMETER_SAMPLE_SIZE = "sample_size"
    SORT_LOG_REQUIRED = "sort_log_required"


def apply(
    dataframe: pl.LazyFrame,
    list_activities: List[str],
    sample_size: int,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> List[List[float]]:
    """Compute the performance spectrum on a Polars LazyFrame."""

    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME
    )
    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY
    )
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, xes.DEFAULT_TIMESTAMP_KEY
    )
    sort_log_required = exec_utils.get_param_value(
        Parameters.SORT_LOG_REQUIRED, parameters, True
    )

    lf = dataframe.select(
        pl.col(case_id_glue),
        pl.col(activity_key).cast(pl.Utf8),
        pl.col(timestamp_key),
    )
    lf = lf.filter(pl.col(activity_key).is_in(list_activities))
    lf = lf.with_row_index(constants.DEFAULT_EVENT_INDEX_KEY)

    if sort_log_required:
        lf = lf.sort([case_id_glue, timestamp_key, constants.DEFAULT_EVENT_INDEX_KEY], maintain_order=True)

    lf = lf.with_columns(
        pl.col(timestamp_key).dt.timestamp().alias(timestamp_key)
    )

    def key(prefix: str, idx: int) -> str:
        return f"{prefix}_{idx}"

    shifted = lf
    for idx in range(len(list_activities)):
        shifted = shifted.with_columns(
            pl.col(activity_key)
            .shift(-idx)
            .over(case_id_glue)
            .alias(key(activity_key, idx)),
            pl.col(timestamp_key)
            .shift(-idx)
            .over(case_id_glue)
            .alias(key(timestamp_key, idx)),
        )

    activity_cols = [key(activity_key, idx) for idx in range(len(list_activities))]
    timestamp_cols = [key(timestamp_key, idx) for idx in range(len(list_activities))]

    pattern_str = "".join(list_activities)

    shifted = shifted.filter(
        pl.all_horizontal([pl.col(col).is_not_null() for col in activity_cols])
    )

    shifted = shifted.with_columns(
        pl.concat_str([pl.col(col) for col in activity_cols]).alias("pattern")
    )

    shifted = shifted.filter(pl.col("pattern") == pattern_str)

    matches = shifted.select([pl.col(col) for col in timestamp_cols]).collect()

    points = []
    for row in matches.iter_rows(named=False):
        points.append([value / 1_000_000 for value in row])

    points.sort(key=lambda x: x[0])

    if len(points) > sample_size:
        points = points[:sample_size]

    return points
