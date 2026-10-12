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
from typing import Any, Dict, List, Optional, Set, Union

import polars as pl

from pm4py.util import constants, points_subset
from pm4py.util import exec_utils
from pm4py.util import xes_constants as xes


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    PARAMETER_SAMPLE_SIZE = "sample_size"
    SORT_LOG_REQUIRED = "sort_log_required"


def gen_patterns(pattern: List[str], length: int) -> List[str]:
    return ["".join(pattern[i : i + length]) for i in range(len(pattern) - (length - 1))]


def _prepare_dataframe(
    lf: pl.LazyFrame,
    activities: List[str],
    case_id_glue: str,
    activity_key: str,
    timestamp_key: str,
    sort_required: bool,
) -> pl.LazyFrame:
    lf = lf.select(
        pl.col(case_id_glue),
        pl.col(activity_key),
        pl.col(timestamp_key),
    )
    lf = lf.filter(pl.col(activity_key).is_in(activities))
    lf = lf.with_row_index(constants.DEFAULT_EVENT_INDEX_KEY)
    if sort_required:
        lf = lf.sort([case_id_glue, timestamp_key, constants.DEFAULT_EVENT_INDEX_KEY], maintain_order=True)
    lf = lf.with_columns(pl.col(timestamp_key).dt.timestamp().alias(timestamp_key))
    return lf


def apply(
    dataframe: pl.LazyFrame,
    list_activities: List[str],
    sample_size: int,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> Dict[str, Any]:
    """Compute disconnected performance spectrum using a Polars LazyFrame."""

    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME
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

    lf = _prepare_dataframe(
        dataframe,
        list_activities,
        case_id_glue,
        activity_key,
        timestamp_key,
        sort_log_required,
    )

    points: List[Dict[str, Any]] = []

    all_patterns = [
        (
            len(list_activities) - i,
            gen_patterns(list_activities, len(list_activities) - i),
        )
        for i in range(len(list_activities) - 1)
    ]

    def key(prefix: str, idx: int) -> str:
        return f"{prefix}_{idx}"

    for length, patterns in all_patterns:
        if length <= 0:
            continue

        pattern_lf = lf
        exprs: List[pl.Expr] = []
        for i in range(length):
            exprs.extend(
                [
                    pl.col(activity_key)
                    .shift(-i)
                    .over(case_id_glue)
                    .alias(key(activity_key, i)),
                    pl.col(timestamp_key)
                    .shift(-i)
                    .over(case_id_glue)
                    .alias(key(timestamp_key, i)),
                    pl.col(constants.DEFAULT_EVENT_INDEX_KEY)
                    .shift(-i)
                    .over(case_id_glue)
                    .alias(key(constants.DEFAULT_EVENT_INDEX_KEY, i)),
                ]
            )

        pattern_lf = pattern_lf.with_columns(exprs)
        pattern_lf = pattern_lf.filter(
            pl.all_horizontal(
                [pl.col(key(activity_key, i)).is_not_null() for i in range(length)]
            )
        )

        pattern_values = ["".join(pat) for pat in patterns]
        if not pattern_values:
            continue

        pattern_lf = pattern_lf.with_columns(
            pl.concat_str([pl.col(key(activity_key, i)) for i in range(length)])
            .alias("pattern")
        )
        pattern_lf = pattern_lf.filter(pl.col("pattern").is_in(pattern_values))

        collected = pattern_lf.collect()
        if collected.height == 0:
            continue

        to_drop_indexes: Set[int] = set()

        for row in collected.iter_rows(named=True):
            activities_seq = [row[key(activity_key, i)] for i in range(length)]
            timestamps_seq = [row[key(timestamp_key, i)] / 1_000_000 for i in range(length)]
            case_id = row[case_id_glue]

            points.append(
                {
                    "case_id": case_id,
                    "points": list(zip(activities_seq, timestamps_seq)),
                }
            )

            for i in range(length - 1):
                to_drop_indexes.add(row[key(constants.DEFAULT_EVENT_INDEX_KEY, i)])

        if to_drop_indexes:
            lf = lf.filter(
                ~pl.col(constants.DEFAULT_EVENT_INDEX_KEY).is_in(
                    pl.lit(list(to_drop_indexes))
                )
            )

    points = sorted(
        points,
        key=lambda entry: min(entry["points"], key=lambda evt: evt[1])[1],
    )

    if len(points) > sample_size:
        points = points_subset.pick_chosen_points_list(sample_size, points)

    return points
