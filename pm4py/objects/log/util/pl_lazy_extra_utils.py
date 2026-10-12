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
from typing import Optional, Dict, Any, Iterable, List, Set

import polars as pl

from pm4py.util import constants, xes_constants, exec_utils


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    COMPUTE_EXTRA_TEMPORAL_FEATURES = "compute_extra_temporal_features"


def _drop_if_present(lf: pl.LazyFrame, cols: Iterable[str]) -> pl.LazyFrame:
    """Drop columns from a LazyFrame if they exist (schema-aware)."""
    existing: Set[str] = set(lf.collect_schema().names())
    to_drop = [c for c in cols if c in existing]
    return lf.drop(to_drop) if to_drop else lf


def _prepare_case_features(
    df: pl.LazyFrame,
    case_id_key: str,
    start_timestamp_key: str,
    timestamp_key: str,
    compute_extra_temporal_features: bool,
) -> pl.LazyFrame:
    """Compute per-case aggregates needed for feature enrichment."""

    # Use more specific internal names to minimize collisions with user columns.
    case_start_col = "__pm4py_case_start"
    case_end_col = "__pm4py_case_end"

    case_summary = df.group_by(case_id_key).agg(
        [
            pl.col(start_timestamp_key).first().alias(case_start_col),
            pl.col(timestamp_key).last().alias(case_end_col),
        ]
    )

    case_summary = case_summary.with_columns(
        (
            (
                pl.col(case_end_col).dt.timestamp("ns")
                - pl.col(case_start_col).dt.timestamp("ns")
            )
            / 1_000_000_000
        ).alias("@@case_throughput")
    )

    if compute_extra_temporal_features:
        case_summary = case_summary.with_columns(
            [
                pl.col(case_start_col).dt.strftime("%Y").alias("@@case_start_year"),
                pl.col(case_start_col).dt.strftime("%Y-%m").alias("@@case_start_ymonth"),
                pl.concat_str(pl.lit("M"), pl.col(case_start_col).dt.strftime("%m")).alias(
                    "@@case_start_month"
                ),
                pl.concat_str(
                    pl.lit("W"),
                    pl.col(case_start_col)
                    .dt.week()
                    .cast(pl.Utf8)
                    .str.pad_start(2, "0"),
                ).alias("@@case_start_week"),
                pl.col(case_end_col).dt.strftime("%Y").alias("@@case_end_year"),
                pl.col(case_end_col).dt.strftime("%Y-%m").alias("@@case_end_ymonth"),
                pl.concat_str(pl.lit("M"), pl.col(case_end_col).dt.strftime("%m")).alias(
                    "@@case_end_month"
                ),
                pl.concat_str(
                    pl.lit("W"),
                    pl.col(case_end_col)
                    .dt.week()
                    .cast(pl.Utf8)
                    .str.pad_start(2, "0"),
                ).alias("@@case_end_week"),
            ]
        )

    select_columns: List[pl.Expr] = [pl.col(case_id_key), pl.col("@@case_throughput")]

    if compute_extra_temporal_features:
        select_columns.extend(
            [
                pl.col("@@case_start_year"),
                pl.col("@@case_start_ymonth"),
                pl.col("@@case_start_month"),
                pl.col("@@case_start_week"),
                pl.col("@@case_end_year"),
                pl.col("@@case_end_ymonth"),
                pl.col("@@case_end_month"),
                pl.col("@@case_end_week"),
            ]
        )

    return case_summary.select(select_columns)


def compute_extra_columns(
    dataframe: pl.LazyFrame,
    parameters: Optional[Dict[Any, Any]] = None,
) -> pl.LazyFrame:
    """Enrich a Polars LazyFrame with additional case-level columns."""

    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME
    )
    start_timestamp_key = exec_utils.get_param_value(
        Parameters.START_TIMESTAMP_KEY,
        parameters,
        xes_constants.DEFAULT_TIMESTAMP_KEY,
    )
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY,
        parameters,
        xes_constants.DEFAULT_TIMESTAMP_KEY,
    )
    compute_extra_temporal_features = exec_utils.get_param_value(
        Parameters.COMPUTE_EXTRA_TEMPORAL_FEATURES, parameters, True
    )

    # Drop any previously-added enrichment columns to avoid duplicated columns
    # (including join-suffix leftovers from older versions).
    all_enrichment_columns = [
        "@@count",
        "@@case_throughput",
        "@@case_start_year",
        "@@case_start_ymonth",
        "@@case_start_month",
        "@@case_start_week",
        "@@case_end_year",
        "@@case_end_ymonth",
        "@@case_end_month",
        "@@case_end_week",
    ]
    drop_candidates = list(all_enrichment_columns) + [
        f"{c}_right" for c in all_enrichment_columns
    ]
    dataframe = _drop_if_present(dataframe, drop_candidates)

    df = dataframe.with_columns(pl.lit(1).alias("@@count"))

    case_features = _prepare_case_features(
        df,
        case_id_key,
        start_timestamp_key,
        timestamp_key,
        compute_extra_temporal_features,
    )

    enriched = df.join(case_features, on=case_id_key, how="left", coalesce=True, maintain_order="left")
    return enriched


__all__ = ["Parameters", "compute_extra_columns"]
