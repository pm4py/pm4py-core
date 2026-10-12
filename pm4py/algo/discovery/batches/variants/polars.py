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
from typing import Optional, Dict, Any, List, Tuple, Union

import polars as pl

from pm4py.algo.discovery.batches.utils import detection
from pm4py.util import exec_utils, constants, xes_constants, pandas_utils


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    RESOURCE_KEY = constants.PARAMETER_CONSTANT_RESOURCE_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    EVENT_ID_KEY = "event_id_key"
    MERGE_DISTANCE = "merge_distance"
    MIN_BATCH_SIZE = "min_batch_size"


def _to_seconds_expr(column_name: str, schema: Dict[str, Any]) -> pl.Expr:
    expr = pl.col(column_name)
    dtype_repr = str(schema[column_name]).lower()
    if "date" in dtype_repr or "time" in dtype_repr:
        return (
            expr.dt.cast_time_unit("ns")
            .dt.timestamp("ns")
            .cast(pl.Float64)
            / 1_000_000_000
        )
    if any(token in dtype_repr for token in ("int", "float")):
        return expr.cast(pl.Float64)
    raise Exception(
        f"Column '{column_name}' must be temporal or numeric to evaluate seconds."
    )


def apply(
    log: pl.LazyFrame,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> List[Tuple[Tuple[str, str], int, Dict[str, Any]]]:
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
    )
    resource_key = exec_utils.get_param_value(
        Parameters.RESOURCE_KEY, parameters, xes_constants.DEFAULT_RESOURCE_KEY
    )
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY,
        parameters,
        xes_constants.DEFAULT_TIMESTAMP_KEY,
    )
    start_timestamp_key = exec_utils.get_param_value(
        Parameters.START_TIMESTAMP_KEY, parameters, timestamp_key
    )
    case_id_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME
    )
    event_id_key = exec_utils.get_param_value(
        Parameters.EVENT_ID_KEY, parameters, constants.DEFAULT_INDEX_KEY
    )

    pandas_utils.check_pandas_dataframe_columns(
        log,
        activity_key=activity_key,
        case_id_key=case_id_key,
        timestamp_key=timestamp_key,
        start_timestamp_key=start_timestamp_key,
    )

    schema = log.collect_schema()
    attributes = [
        activity_key,
        resource_key,
        start_timestamp_key,
        timestamp_key,
        case_id_key,
    ]
    log_contains_evidkey = event_id_key in schema
    if log_contains_evidkey:
        attributes.append(event_id_key)

    # ensure attribute order without duplicates
    seen = set()
    ordered_attributes: List[str] = []
    for attr in attributes:
        if attr not in seen:
            seen.add(attr)
            ordered_attributes.append(attr)

    lf = log.select([pl.col(col) for col in ordered_attributes])

    lf = lf.with_columns(
        [
            _to_seconds_expr(start_timestamp_key, schema).alias("__pm4py_start_sec__"),
            _to_seconds_expr(timestamp_key, schema).alias("__pm4py_complete_sec__"),
        ]
    )

    lf = lf.with_row_index("__pm4py_order__")

    aggregation_exprs = [
        pl.col("__pm4py_start_sec__")
        .sort_by("__pm4py_order__")
        .alias("__pm4py_start__"),
        pl.col("__pm4py_complete_sec__")
        .sort_by("__pm4py_order__")
        .alias("__pm4py_complete__"),
        pl.col(case_id_key)
        .sort_by("__pm4py_order__")
        .alias("__pm4py_cases__"),
    ]

    if log_contains_evidkey:
        aggregation_exprs.append(
            pl.col(event_id_key)
            .sort_by("__pm4py_order__")
            .alias("__pm4py_events__")
        )

    grouped = (
        lf.group_by(activity_key, resource_key, maintain_order=True)
        .agg(aggregation_exprs)
        .collect()
    )

    actres_grouping: Dict[Tuple[str, str], List[Tuple[Any, ...]]] = {}

    for row in grouped.iter_rows(named=True):
        key = (row[activity_key], row[resource_key])
        starts = list(row["__pm4py_start__"])
        completes = list(row["__pm4py_complete__"])
        cases = list(row["__pm4py_cases__"])
        events_list = (
            list(row["__pm4py_events__"])
            if log_contains_evidkey
            else None
        )

        batches = []
        for idx in range(len(starts)):
            entry: Tuple[Any, ...]
            if log_contains_evidkey and events_list is not None:
                entry = (starts[idx], completes[idx], cases[idx], events_list[idx])
            else:
                entry = (starts[idx], completes[idx], cases[idx])
            batches.append(entry)

        actres_grouping[key] = batches

    return detection.detect(actres_grouping, parameters=parameters)
