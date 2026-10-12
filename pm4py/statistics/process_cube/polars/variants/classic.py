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

from bisect import bisect_right
import math
from enum import Enum
from typing import Optional, Dict, Any, Tuple, List, Union
from itertools import product

import numpy as np
import polars as pl

from pm4py.util import constants, exec_utils

CASE_ID_COL = constants.CASE_CONCEPT_NAME

# Accepted aggregate functions for Polars pivot
_AGG_FN_ALIASES = {
    "avg": "mean",
    "average": "mean",
    "mean": "mean",
    "sum": "sum",
    "min": "min",
    "max": "max",
    "count": "count",
    "len": "count",
    "median": "median",
    "first": "first",
    "last": "last",
}


class Parameters(Enum):
    MAX_DIVISIONS_X = "max_divisions_x"
    MAX_DIVISIONS_Y = "max_divisions_y"
    AGGREGATION_FUNCTION = "aggregation_function"
    X_BINS = "x_bins"
    Y_BINS = "y_bins"


_NUMERIC_DTYPES = {
    pl.Int8,
    pl.Int16,
    pl.Int32,
    pl.Int64,
    pl.UInt8,
    pl.UInt16,
    pl.UInt32,
    pl.UInt64,
    pl.Float32,
    pl.Float64,
}


def _ensure_polars_df(
    feature_table: Union[pl.LazyFrame, pl.DataFrame],
    required_columns: Optional[List[str]] = None,
) -> pl.DataFrame:
    if required_columns is None:
        required_columns = []
    if isinstance(feature_table, pl.LazyFrame):
        if required_columns:
            return feature_table.select(required_columns).collect()
        return feature_table.collect()
    if isinstance(feature_table, pl.DataFrame):
        if required_columns:
            return feature_table.select(required_columns).clone()
        return feature_table.clone()
    raise TypeError(
        "feature_table must be a Polars LazyFrame or DataFrame"
    )


def _available_columns(
    feature_table: Union[pl.LazyFrame, pl.DataFrame]
) -> List[str]:
    if isinstance(feature_table, pl.LazyFrame):
        return feature_table.collect_schema().names()
    if isinstance(feature_table, pl.DataFrame):
        return feature_table.columns
    raise TypeError(
        "feature_table must be a Polars LazyFrame or DataFrame"
    )


def _dedupe_columns(columns: List[str]) -> List[str]:
    seen = set()
    deduped: List[str] = []
    for column in columns:
        if column not in seen:
            seen.add(column)
            deduped.append(column)
    return deduped


def _dimension_required_columns(
    available_columns: List[str],
    dim: Union[str, Tuple[str, ...]],
) -> List[str]:
    resolved: List[str] = []
    available_set = set(available_columns)
    for column in _normalize_dimension(dim):
        if column in available_set:
            resolved.append(column)
        else:
            resolved.extend(
                candidate
                for candidate in available_columns
                if candidate.startswith(column + "_")
            )
    return _dedupe_columns(resolved)


def _required_feature_columns(
    feature_table: Union[pl.LazyFrame, pl.DataFrame],
    x_col: Union[str, Tuple[str, ...]],
    y_col: Union[str, Tuple[str, ...]],
    agg_col: str,
) -> List[str]:
    available_columns = _available_columns(feature_table)
    available_set = set(available_columns)
    required_columns: List[str] = []

    for column in (CASE_ID_COL, agg_col):
        if column in available_set:
            required_columns.append(column)

    required_columns.extend(
        _dimension_required_columns(available_columns, x_col)
    )
    required_columns.extend(
        _dimension_required_columns(available_columns, y_col)
    )

    return _dedupe_columns(required_columns)


def _is_numeric_dtype(dtype: pl.DataType) -> bool:
    if dtype in _NUMERIC_DTYPES:
        return True
    dtype_str = str(dtype).lower()
    return any(token in dtype_str for token in ("int", "uint", "float"))


def _prepare_bins(
    series: pl.Series,
    manual_bins: Optional[List[float]],
    max_divisions: int,
) -> List[float]:
    if manual_bins:
        bins = sorted(set(float(b) for b in manual_bins))
        if len(bins) >= 2:
            return bins

    values = series.drop_nulls()
    if values.is_empty():
        return []

    min_val = float(values.min())
    max_val = float(values.max())
    if math.isfinite(min_val) and math.isfinite(max_val):
        if math.isclose(min_val, max_val):
            return [min_val - 0.5, max_val + 0.5]

        max_divisions = max(int(max_divisions), 1)
        bins_array = np.linspace(min_val, max_val, max_divisions + 1)
        bins = sorted(set(float(b) for b in bins_array))
        if len(bins) >= 2:
            return bins
        return [min_val - 0.5, max_val + 0.5]

    return []


def _bin_labels(bins: List[float]) -> List[str]:
    if len(bins) < 2:
        return []
    return [f"[{bins[i]}, {bins[i + 1]}]" for i in range(len(bins) - 1)]


def _assign_bins(series: pl.Series, bins: List[float], name: str) -> pl.Series:
    length = len(series)
    if len(bins) < 2:
        return pl.Series(name, [None] * length)

    labels = _bin_labels(bins)
    last_edge = bins[-1]

    assigned: List[Optional[str]] = []
    for value in series.to_list():
        if value is None:
            assigned.append(None)
            continue
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            assigned.append(None)
            continue
        if not math.isfinite(numeric_value):
            assigned.append(None)
            continue

        idx = bisect_right(bins, numeric_value) - 1
        if idx == len(labels) and math.isclose(numeric_value, last_edge, rel_tol=1e-9, abs_tol=1e-9):
            idx -= 1
        if idx < 0 or idx >= len(labels):
            assigned.append(None)
        else:
            assigned.append(labels[idx])

    return pl.Series(name, assigned)


def _normalize_agg_fn(agg_fn: Any) -> str:
    if isinstance(agg_fn, str):
        key = agg_fn.lower()
        return _AGG_FN_ALIASES.get(key, key)
    return "mean"


def _aggregation_expression(column: str, agg_fn: str) -> pl.Expr:
    if agg_fn == "sum":
        return pl.col(column).sum()
    if agg_fn == "min":
        return pl.col(column).min()
    if agg_fn == "max":
        return pl.col(column).max()
    if agg_fn == "median":
        return pl.col(column).median()
    if agg_fn == "first":
        return pl.col(column).first()
    if agg_fn == "last":
        return pl.col(column).last()
    if agg_fn == "count":
        return pl.len()
    # default mean
    return pl.col(column).mean()


def _prefix_columns(df: pl.DataFrame, prefix: str) -> List[str]:
    return [col for col in df.columns if col.startswith(prefix + "_")]


def _normalize_dimension(dim: Union[str, Tuple[str, ...]]) -> Tuple[str, ...]:
    if isinstance(dim, tuple):
        return dim
    return (dim,)


def _select_bins_param(
    bins_param: Any,
    idx: int,
    col: str,
    num_dims: int,
) -> Optional[List[float]]:
    if bins_param is None:
        return None
    if isinstance(bins_param, dict):
        if col in bins_param:
            return bins_param[col]
        if idx in bins_param:
            return bins_param[idx]
        return None
    if isinstance(bins_param, (list, tuple)) and num_dims > 1:
        if len(bins_param) == num_dims and all(
            isinstance(item, (list, tuple)) for item in bins_param
        ):
            return list(bins_param[idx])
    return bins_param


def _combine_bins(dim_cols: Tuple[str, ...], bins_per_dim: List[List[str]]) -> List[str]:
    if not bins_per_dim:
        return []
    if len(bins_per_dim) == 1:
        return bins_per_dim[0]
    combined: List[str] = []
    for combo in product(*bins_per_dim):
        parts = [f"{dim_cols[i]}={combo[i]}" for i in range(len(dim_cols))]
        combined.append(" | ".join(parts))
    return combined


def _dimension_bins(
    df: pl.DataFrame,
    dim: Union[str, Tuple[str, ...]],
    bins_param: Any,
    max_divisions: int,
    dim_name: str,
) -> Tuple[pl.DataFrame, List[str]]:
    dim_cols = _normalize_dimension(dim)
    if not dim_cols:
        return pl.DataFrame(), []

    per_attr_dfs: List[pl.DataFrame] = []
    bins_per_dim: List[List[str]] = []

    for idx, col in enumerate(dim_cols):
        col_exists = col in df.columns
        numeric = col_exists and _is_numeric_dtype(df.schema[col])
        bin_col = f"__bin_{idx}"

        if numeric:
            selected_bins = _select_bins_param(bins_param, idx, col, len(dim_cols))
            bins = _prepare_bins(df[col], selected_bins, max_divisions)
            if len(bins) < 2:
                return pl.DataFrame(), []
            bins_per_dim.append(_bin_labels(bins))

            series = _assign_bins(df[col], bins, bin_col)
            attr_df = (
                df.select([CASE_ID_COL])
                .with_columns(series)
                .filter(pl.col(bin_col).is_not_null())
                .select([CASE_ID_COL, pl.col(bin_col)])
            )
        else:
            prefix_cols = _prefix_columns(df, col)
            if prefix_cols:
                bins_per_dim.append(prefix_cols)
                attr_df = (
                    df.select([CASE_ID_COL, *prefix_cols])
                    .unpivot(
                        index=[CASE_ID_COL],
                        on=prefix_cols,
                        variable_name=bin_col,
                        value_name="__value",
                    )
                    .filter(pl.col("__value").fill_null(0) >= 1)
                    .select([CASE_ID_COL, pl.col(bin_col)])
                )
            elif col_exists:
                series = df[col].cast(pl.Utf8)
                bins = (
                    series.drop_nulls()
                    .unique()
                    .sort()
                    .to_list()
                )
                if not bins:
                    return pl.DataFrame(), []
                bins_per_dim.append([str(b) for b in bins])
                attr_df = (
                    df.select([CASE_ID_COL])
                    .with_columns(series.alias(bin_col))
                    .filter(pl.col(bin_col).is_not_null())
                    .select([CASE_ID_COL, pl.col(bin_col)])
                )
            else:
                return pl.DataFrame(), []

        if attr_df.is_empty():
            return pl.DataFrame(), []
        per_attr_dfs.append(attr_df)

    combined = per_attr_dfs[0]
    for attr_df in per_attr_dfs[1:]:
        combined = combined.join(attr_df, on=CASE_ID_COL, how="inner", maintain_order="left")
        if combined.is_empty():
            return pl.DataFrame(), []

    bin_cols = [f"__bin_{idx}" for idx in range(len(dim_cols))]
    if len(bin_cols) == 1:
        combined = combined.with_columns(
            pl.col(bin_cols[0]).alias(f"{dim_name}_bin")
        )
        all_bins = bins_per_dim[0]
    else:
        label_parts = [
            pl.concat_str([pl.lit(f"{dim_cols[i]}="), pl.col(bin_cols[i])], separator="")
            for i in range(len(dim_cols))
        ]
        combined = combined.with_columns(
            pl.concat_str(label_parts, separator=" | ").alias(f"{dim_name}_bin")
        )
        all_bins = _combine_bins(dim_cols, bins_per_dim)

    return combined.select([CASE_ID_COL, f"{dim_name}_bin"]), all_bins


def _numeric_numeric_case(
    df: pl.DataFrame,
    x_col: str,
    y_col: str,
    agg_col: str,
    x_bins: List[float],
    y_bins: List[float],
) -> pl.DataFrame:
    x_bin_series = _assign_bins(df[x_col], x_bins, "x_bin")
    y_bin_series = _assign_bins(df[y_col], y_bins, "y_bin")

    df = df.with_columns([x_bin_series, y_bin_series])

    temp_df = (
        df.filter(pl.col("x_bin").is_not_null() & pl.col("y_bin").is_not_null())
        .select([pl.col(CASE_ID_COL), pl.col("x_bin"), pl.col("y_bin"), pl.col(agg_col)])
    )
    return temp_df


def _numeric_prefix_case(
    df: pl.DataFrame,
    x_col: str,
    agg_col: str,
    bins: List[float],
    prefix_cols: List[str],
    prefix_label: str,
) -> pl.DataFrame:
    x_bin_series = _assign_bins(df[x_col], bins, "x_bin")
    df = df.with_columns(x_bin_series)

    if not prefix_cols:
        return pl.DataFrame({CASE_ID_COL: [], "x_bin": [], "y_bin": [], agg_col: []})

    melted = (
        df.select([CASE_ID_COL, agg_col, "x_bin", *prefix_cols])
        .unpivot(
            index=[CASE_ID_COL, agg_col, "x_bin"],
            on=prefix_cols,
            variable_name=prefix_label,
            value_name="__value",
        )
        .filter(pl.col("x_bin").is_not_null() & (pl.col("__value").fill_null(0) >= 1))
        .select([
            pl.col(CASE_ID_COL),
            pl.col("x_bin"),
            pl.col(prefix_label).alias("y_bin"),
            pl.col(agg_col),
        ])
    )
    return melted


def _prefix_numeric_case(
    df: pl.DataFrame,
    y_col: str,
    agg_col: str,
    bins: List[float],
    prefix_cols: List[str],
    prefix_label: str,
) -> pl.DataFrame:
    y_bin_series = _assign_bins(df[y_col], bins, "y_bin")
    df = df.with_columns(y_bin_series)

    if not prefix_cols:
        return pl.DataFrame({CASE_ID_COL: [], "x_bin": [], "y_bin": [], agg_col: []})

    melted = (
        df.select([CASE_ID_COL, agg_col, "y_bin", *prefix_cols])
        .unpivot(
            index=[CASE_ID_COL, agg_col, "y_bin"],
            on=prefix_cols,
            variable_name=prefix_label,
            value_name="__value",
        )
        .filter(pl.col("y_bin").is_not_null() & (pl.col("__value").fill_null(0) >= 1))
        .select([
            pl.col(CASE_ID_COL),
            pl.col(prefix_label).alias("x_bin"),
            pl.col("y_bin"),
            pl.col(agg_col),
        ])
    )
    return melted


def _prefix_prefix_case(
    df: pl.DataFrame,
    agg_col: str,
    x_prefix_cols: List[str],
    y_prefix_cols: List[str],
) -> pl.DataFrame:
    if not x_prefix_cols or not y_prefix_cols:
        return pl.DataFrame({CASE_ID_COL: [], "x_bin": [], "y_bin": [], agg_col: []})

    x_melt = (
        df.select([CASE_ID_COL, agg_col, *x_prefix_cols])
        .unpivot(
            index=[CASE_ID_COL, agg_col],
            on=x_prefix_cols,
            variable_name="x_bin",
            value_name="__x_value",
        )
        .filter(pl.col("__x_value").fill_null(0) >= 1)
        .select([pl.col(CASE_ID_COL), pl.col("x_bin"), pl.col(agg_col)])
    )

    y_melt = (
        df.select([CASE_ID_COL, *y_prefix_cols])
        .unpivot(
            index=[CASE_ID_COL],
            on=y_prefix_cols,
            variable_name="y_bin",
            value_name="__y_value",
        )
        .filter(pl.col("__y_value").fill_null(0) >= 1)
        .select([pl.col(CASE_ID_COL), pl.col("y_bin")])
    )

    temp_df = (
        x_melt.join(y_melt, on=CASE_ID_COL, how="inner", maintain_order="left")
        .select([pl.col(CASE_ID_COL), pl.col("x_bin"), pl.col("y_bin"), pl.col(agg_col)])
    )
    return temp_df


def apply(
    feature_table: Union[pl.LazyFrame, pl.DataFrame],
    x_col: Union[str, Tuple[str, ...]],
    y_col: Union[str, Tuple[str, ...]],
    agg_col: str,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Tuple[pl.DataFrame, Dict[Any, Any]]:
    """Construct a process cube using Polars data structures.

    The X/Y dimensions can be defined by a single attribute (str) or by a tuple of
    attributes. When a tuple is provided, bins are computed per attribute and then
    combined into a single composite bin label.
    """

    if parameters is None:
        parameters = {}

    required_columns = _required_feature_columns(feature_table, x_col, y_col, agg_col)
    df = _ensure_polars_df(feature_table, required_columns=required_columns)
    if df.is_empty():
        return pl.DataFrame(), {}

    agg_fn_param = exec_utils.get_param_value(
        Parameters.AGGREGATION_FUNCTION, parameters, "mean"
    )
    agg_fn = _normalize_agg_fn(agg_fn_param)

    max_divisions_x = exec_utils.get_param_value(Parameters.MAX_DIVISIONS_X, parameters, 4)
    max_divisions_y = exec_utils.get_param_value(Parameters.MAX_DIVISIONS_Y, parameters, 4)
    x_bins_param = exec_utils.get_param_value(Parameters.X_BINS, parameters, None)
    y_bins_param = exec_utils.get_param_value(Parameters.Y_BINS, parameters, None)

    x_dim_df, all_x_bins = _dimension_bins(
        df, x_col, x_bins_param, max_divisions_x, "x"
    )
    if x_dim_df.is_empty():
        return pl.DataFrame(), {}

    y_dim_df, all_y_bins = _dimension_bins(
        df, y_col, y_bins_param, max_divisions_y, "y"
    )
    if y_dim_df.is_empty():
        return pl.DataFrame(), {}

    temp_df = (
        x_dim_df.join(y_dim_df, on=CASE_ID_COL, how="inner", maintain_order="left")
        .join(df.select([CASE_ID_COL, agg_col]), on=CASE_ID_COL, how="inner", maintain_order="left")
    )

    if temp_df.is_empty():
        return pl.DataFrame(), {}

    temp_df = temp_df.filter(
        pl.col("x_bin").is_not_null() & pl.col("y_bin").is_not_null()
    )
    if temp_df.is_empty():
        return pl.DataFrame(), {}

    agg_expr = _aggregation_expression(agg_col, agg_fn).alias("value")
    grouped_values = (
        temp_df.group_by(["x_bin", "y_bin"], maintain_order=True)
        .agg(agg_expr)
    )

    pivot_df = grouped_values.pivot(
        values="value",
        index="x_bin",
        on="y_bin",
        sort_columns=False,
    )

    if all_x_bins:
        base_rows = pl.DataFrame({"x_bin": all_x_bins})
        pivot_df = base_rows.join(pivot_df, on="x_bin", how="left", maintain_order="left")

    value_columns = [col for col in pivot_df.columns if col != "x_bin"]
    if all_y_bins:
        missing_cols = [col for col in all_y_bins if col not in value_columns]
        if missing_cols:
            additions = {col: [None] * pivot_df.height for col in missing_cols}
            pivot_df = pl.concat([pivot_df, pl.DataFrame(additions)], how="horizontal")
        ordered_cols = ["x_bin", *all_y_bins]
        remaining_cols = [col for col in pivot_df.columns if col not in ordered_cols]
        pivot_df = pivot_df.select([*ordered_cols, *remaining_cols])

    case_groups = (
        temp_df.group_by(["x_bin", "y_bin"], maintain_order=True)
        .agg(pl.col(CASE_ID_COL).unique().alias("case_ids"))
    )
    cell_case_dict = {
        (row[0], row[1]): set(row[2])
        for row in case_groups.iter_rows()
    }

    return pivot_df, cell_case_dict


__all__ = ["Parameters", "apply"]
