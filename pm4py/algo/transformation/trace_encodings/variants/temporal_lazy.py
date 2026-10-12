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
from typing import Optional, Dict, Any

from pm4py.util import exec_utils, constants, xes_constants, pandas_utils


class Parameters(Enum):
    ARRIVAL_RATE = "arrival_rate"
    FINISH_RATE = "finish_rate"
    CASE_ID_COLUMN = constants.PARAMETER_CONSTANT_CASEID_KEY
    START_TIMESTAMP_COLUMN = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_COLUMN = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    RESOURCE_COLUMN = constants.PARAMETER_CONSTANT_RESOURCE_KEY
    ACTIVITY_COLUMN = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    GROUPER_FREQ = "grouper_freq"
    SERVICE_TIME = "service_time"
    WAITING_TIME = "waiting_time"
    SOJOURN_TIME = "sojourn_time"
    DIFF_START_END = "diff_start_end"


_WINDOW_START_COL = "__window_start"


def _freq_to_polars_duration(freq: str) -> str:
    """
    Convert a pandas-style frequency string to a Polars duration string.
    """
    if not freq:
        raise ValueError("grouper frequency must be a non-empty string")

    freq = freq.strip()
    freq_upper = freq.upper()
    # Remove timezone/day designators (e.g., W-MON -> W)
    if "-" in freq_upper:
        freq_upper = freq_upper.split("-", 1)[0]

    numbers = "".join(ch for ch in freq_upper if ch.isdigit())
    letters = "".join(ch for ch in freq_upper if ch.isalpha())

    if not letters:
        raise ValueError(f"cannot infer unit from grouper frequency '{freq}'")

    if not numbers:
        numbers = "1"

    normalized_unit = letters
    if normalized_unit in {"MIN"}:
        normalized_unit = "MIN"
    else:
        # Drop suffixes such as S, E (month/quarter/year start/end)
        normalized_unit = normalized_unit.rstrip("S").rstrip("E")
        if not normalized_unit:
            normalized_unit = letters

    unit_mapping = {
        "S": "s",
        "SEC": "s",
        "SECOND": "s",
        "MIN": "m",
        "T": "m",
        "H": "h",
        "D": "d",
        "W": "w",
        "M": "mo",
        "Q": "q",
        "Y": "y",
        "A": "y",
    }

    if normalized_unit not in unit_mapping:
        raise ValueError(
            f"grouper frequency '{freq}' is not supported when using the temporal_lazy variant."
        )

    return f"{numbers}{unit_mapping[normalized_unit]}"


def apply(
    log,
    parameters: Optional[Dict[Any, Any]] = None,
):
    """
    Aggregates a Polars LazyFrame event log into temporal windows.

    This is the lazy Polars equivalent of the temporal variant. From an
    event-log point of view, events are grouped by timestamp windows and each
    output row describes one window. The returned LazyFrame contains the same
    feature semantics as the pandas temporal variant, such as unique
    resources, unique activities, number of events, average waiting/service
    times, rework counts, and cases/resources per window.

    Example with GROUPER_FREQ="D":
        day 2024-01-01 has 2 cases and 5 events
        day 2024-01-02 has 1 case and 2 events

    The result is a lazy query that, when collected, yields two rows with
    window-level feature values.

    Parameters
    ----------------
    log
        Polars LazyFrame containing the event log
    parameters
        Parameters of the algorithm (same semantics as the pandas-based temporal variant)

    Returns
    ----------------
    pl.DataFrame
        Dataframe with temporal features, aggregated per time window
    """
    if parameters is None:
        parameters = {}

    import polars as pl

    if not pandas_utils.is_polars_lazyframe(log):
        raise TypeError(
            "temporal_lazy.apply expects a Polars LazyFrame as input."
        )

    grouper_freq = exec_utils.get_param_value(
        Parameters.GROUPER_FREQ, parameters, "W"
    )
    timestamp_column = exec_utils.get_param_value(
        Parameters.TIMESTAMP_COLUMN,
        parameters,
        xes_constants.DEFAULT_TIMESTAMP_KEY,
    )
    start_timestamp_column = exec_utils.get_param_value(
        Parameters.START_TIMESTAMP_COLUMN, parameters, None
    )
    if start_timestamp_column is None:
        start_timestamp_column = timestamp_column

    case_id_column = exec_utils.get_param_value(
        Parameters.CASE_ID_COLUMN, parameters, constants.CASE_CONCEPT_NAME
    )
    diff_start_end = exec_utils.get_param_value(
        Parameters.DIFF_START_END, parameters, "@@diff_start_end"
    )
    arrival_rate = exec_utils.get_param_value(
        Parameters.ARRIVAL_RATE, parameters, "@@arrival_rate"
    )
    finish_rate = exec_utils.get_param_value(
        Parameters.FINISH_RATE, parameters, "@@finish_rate"
    )
    service_time = exec_utils.get_param_value(
        Parameters.SERVICE_TIME, parameters, "@@service_time"
    )
    waiting_time = exec_utils.get_param_value(
        Parameters.WAITING_TIME, parameters, "@@waiting_time"
    )
    sojourn_time = exec_utils.get_param_value(
        Parameters.SOJOURN_TIME, parameters, "@@sojourn_time"
    )
    resource_column = exec_utils.get_param_value(
        Parameters.RESOURCE_COLUMN,
        parameters,
        xes_constants.DEFAULT_RESOURCE_KEY,
    )
    activity_column = exec_utils.get_param_value(
        Parameters.ACTIVITY_COLUMN, parameters, xes_constants.DEFAULT_NAME_KEY
    )

    lazy_log = pandas_utils.insert_case_arrival_finish_rate(
        log,
        case_id_column=case_id_column,
        timestamp_column=timestamp_column,
        start_timestamp_column=start_timestamp_column,
        arrival_rate_column=arrival_rate,
        finish_rate_column=finish_rate,
    )

    lazy_log = pandas_utils.insert_case_service_waiting_time(
        lazy_log,
        case_id_column=case_id_column,
        timestamp_column=timestamp_column,
        start_timestamp_column=start_timestamp_column,
        diff_start_end_column=diff_start_end,
        service_time_column=service_time,
        sojourn_time_column=sojourn_time,
        waiting_time_column=waiting_time,
    )

    duration = _freq_to_polars_duration(grouper_freq)

    lazy_log = lazy_log.with_columns(
        pl.col(start_timestamp_column)
        .dt.truncate(duration)
        .alias(_WINDOW_START_COL)
    )

    case_agg = (
        lazy_log.group_by([_WINDOW_START_COL, case_id_column])
        .agg(
            pl.len().alias("__events_per_case"),
            pl.col(activity_column)
            .drop_nulls()
            .n_unique()
            .alias("__unique_acts_per_case"),
            pl.col(resource_column)
            .drop_nulls()
            .n_unique()
            .alias("__unique_res_per_case"),
            pl.col(arrival_rate).first().alias("__arrival_rate"),
            pl.col(finish_rate).first().alias("__finish_rate"),
            pl.col(waiting_time).first().alias("__waiting_time"),
            pl.col(sojourn_time).first().alias("__sojourn_time"),
            pl.col(service_time).first().alias("__service_time"),
        )
        .with_columns(
            (
                pl.col("__events_per_case")
                - pl.col("__unique_acts_per_case")
            ).alias("__reworks_per_case")
        )
    )

    case_window = case_agg.group_by(_WINDOW_START_COL).agg(
        pl.col("__reworks_per_case")
        .sum()
        .alias("total_number_of_reworked_activities"),
        pl.col("__events_per_case").mean().alias("avg_events_per_case"),
        pl.col("__unique_res_per_case").mean().alias("avg_resources_per_case"),
        pl.col(case_id_column).n_unique().alias("number_of_cases"),
        pl.col("__arrival_rate").mean().alias("average_arrival_rate"),
        pl.col("__finish_rate").mean().alias("average_finish_rate"),
        pl.col("__waiting_time").mean().alias("average_waiting_time"),
        pl.col("__sojourn_time").mean().alias("average_sojourn_time"),
        pl.col("__service_time").mean().alias("average_service_time"),
    )

    resource_agg = (
        lazy_log.filter(pl.col(resource_column).is_not_null())
        .group_by([_WINDOW_START_COL, resource_column])
        .agg(
            pl.col(case_id_column)
            .n_unique()
            .alias("__cases_per_resource")
        )
    )

    resource_window = resource_agg.group_by(_WINDOW_START_COL).agg(
        pl.col("__cases_per_resource")
        .mean()
        .alias("avg_cases_per_resource")
    )

    basic_window = lazy_log.group_by(_WINDOW_START_COL).agg(
        pl.col(resource_column)
        .drop_nulls()
        .n_unique()
        .alias("unique_resources"),
        pl.col(activity_column)
        .drop_nulls()
        .n_unique()
        .alias("unique_activities"),
        pl.len().alias("num_events"),
    )

    result_lazy = (
        basic_window.join(case_window, on=_WINDOW_START_COL, how="left", maintain_order="left")
        .join(resource_window, on=_WINDOW_START_COL, how="left", maintain_order="left")
        .sort(_WINDOW_START_COL)
        .rename({_WINDOW_START_COL: "timestamp"})
        .with_columns(
            [
                pl.col("total_number_of_reworked_activities").fill_null(0),
                pl.col("avg_events_per_case").fill_null(0),
                pl.col("avg_resources_per_case").fill_null(0),
                pl.col("average_arrival_rate").fill_null(0),
                pl.col("average_finish_rate").fill_null(0),
                pl.col("average_waiting_time").fill_null(0),
                pl.col("average_sojourn_time").fill_null(0),
                pl.col("average_service_time").fill_null(0),
                pl.col("avg_cases_per_resource").fill_null(0),
                pl.col("number_of_cases").fill_null(0),
                pl.col("unique_resources").fill_null(0),
                pl.col("unique_activities").fill_null(0),
                pl.col("num_events").fill_null(0),
            ]
        )
        .select(
            [
                "timestamp",
                "unique_resources",
                "unique_activities",
                "num_events",
                "average_arrival_rate",
                "average_finish_rate",
                "average_waiting_time",
                "average_sojourn_time",
                "average_service_time",
                "total_number_of_reworked_activities",
                "avg_cases_per_resource",
                "avg_events_per_case",
                "number_of_cases",
                "avg_resources_per_case",
            ]
        )
    )

    return result_lazy
