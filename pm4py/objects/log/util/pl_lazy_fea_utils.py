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
from typing import Optional, Dict, Any, List, Set, Iterable, Collection

import polars as pl

from pm4py.objects.log.util.dataframe_utils import Parameters
from pm4py.util import constants, exec_utils, pandas_utils
from pm4py.util import xes_constants


def _dedupe_preserve_order(values: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []
    for v in values:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def _sanitize_feature_name(
    prefix: str, value: Any, used_names: Optional[Set[str]] = None
) -> str:
    sanitized = str(value).encode("ascii", errors="ignore").decode("ascii")
    if not sanitized:
        sanitized = "value"
    base_name = f"{prefix}_{sanitized}"

    if used_names is None:
        return base_name

    candidate = base_name
    suffix = 1
    while candidate in used_names:
        candidate = f"{base_name}__{suffix}"
        suffix += 1
    used_names.add(candidate)
    return candidate


_DEFAULT_NUMERIC_ATTRIBUTE_AGGREGATIONS = (
    "last",
    "first",
    "min",
    "max",
    "mean",
    "median",
    "stdev",
    "sum",
)

_NUMERIC_ATTRIBUTE_AGGREGATION_SUFFIXES = {
    "last": "LAST",
    "first": "FIRST",
    "min": "MIN",
    "max": "MAX",
    "mean": "MEAN",
    "median": "MEDIAN",
    "stdev": "STDEV",
    "sum": "SUM",
}

_NUMERIC_ATTRIBUTE_AGGREGATION_ALIASES = {
    "std": "stdev",
    "standard_deviation": "stdev",
}


def _is_internal_attribute(column: str) -> bool:
    return str(column).startswith("@@")


def _normalize_numeric_attribute_aggregations(
    aggregations: Optional[Collection[str]],
) -> List[str]:
    if aggregations is None:
        values = list(_DEFAULT_NUMERIC_ATTRIBUTE_AGGREGATIONS)
    elif isinstance(aggregations, str):
        values = [aggregations]
    else:
        values = list(aggregations)

    normalized = []
    seen = set()
    for value in values:
        aggregation = str(value).lower()
        aggregation = _NUMERIC_ATTRIBUTE_AGGREGATION_ALIASES.get(
            aggregation, aggregation
        )
        if aggregation not in _NUMERIC_ATTRIBUTE_AGGREGATION_SUFFIXES:
            supported = ", ".join(_DEFAULT_NUMERIC_ATTRIBUTE_AGGREGATIONS)
            raise ValueError(
                f"Unsupported numeric attribute aggregation: {value}. "
                f"Supported values are: {supported}."
            )
        if aggregation not in seen:
            normalized.append(aggregation)
            seen.add(aggregation)

    if isinstance(aggregations, (set, frozenset)):
        normalized_set = set(normalized)
        normalized = [
            aggregation
            for aggregation in _DEFAULT_NUMERIC_ATTRIBUTE_AGGREGATIONS
            if aggregation in normalized_set
        ]

    return normalized


def _get_numeric_feature_columns(
    numeric_columns: List[str],
    enable_numeric_attribute_statistics: bool,
    numeric_attribute_aggregations: Optional[Collection[str]] = None,
) -> List[str]:
    if (
        not enable_numeric_attribute_statistics
        and numeric_attribute_aggregations is None
    ):
        return numeric_columns
    numeric_attribute_aggregations = _normalize_numeric_attribute_aggregations(
        numeric_attribute_aggregations
    )
    feature_columns = []
    for col in numeric_columns:
        if _is_internal_attribute(col):
            feature_columns.append(col)
        else:
            feature_columns.extend(
                f"{col}_{_NUMERIC_ATTRIBUTE_AGGREGATION_SUFFIXES[aggregation]}"
                for aggregation in numeric_attribute_aggregations
            )
    return feature_columns


def _scalar_from_lazy(lf: pl.LazyFrame, expr: pl.Expr) -> Any:
    result = lf.select(expr.alias("__scalar")).collect()
    if result.height == 0 or result.width == 0:
        return None
    return result.to_series(0)[0]


def _lazy_schema(lf: pl.LazyFrame) -> pl.Schema:
    return lf.collect_schema()


def _lazy_columns(lf: pl.LazyFrame) -> List[str]:
    return _lazy_schema(lf).names()


def _drop_if_present(lf: pl.LazyFrame, cols: Iterable[str]) -> pl.LazyFrame:
    existing = set(_lazy_columns(lf))
    to_drop = [c for c in cols if c in existing]
    return lf.drop(to_drop) if to_drop else lf


def _unique_internal_name(existing: Set[str], base: str) -> str:
    if base not in existing:
        return base
    i = 1
    while f"{base}__{i}" in existing:
        i += 1
    return f"{base}__{i}"


def _is_numeric_dtype(dtype: pl.DataType) -> bool:
    dtype_str = str(dtype).lower()
    if any(token in dtype_str for token in ("int", "uint", "float")):
        return True
    if dtype_str.startswith("decimal"):
        return True
    if dtype_str.startswith("duration"):
        return True
    if dtype_str == "boolean":
        return True
    return False


def _is_string_dtype(dtype: pl.DataType) -> bool:
    dtype_str = str(dtype).lower()
    return dtype_str in {"utf8", "string"} or dtype_str.startswith("categorical")


def _numeric_feature_dtype(dtype: pl.DataType) -> pl.DataType:
    if dtype == pl.Boolean:
        return pl.UInt8
    if dtype in {
        pl.Int8,
        pl.Int16,
        pl.Int32,
        pl.UInt8,
        pl.UInt16,
        pl.UInt32,
        pl.Float32,
    }:
        return dtype

    dtype_str = str(dtype).lower()
    if dtype in {pl.Int64, pl.UInt64, pl.Float64}:
        return pl.Float32
    if dtype_str.startswith("decimal") or dtype_str.startswith("duration"):
        return pl.Float32

    return pl.Float32


def _unsigned_count_dtype(max_value: int) -> pl.DataType:
    if max_value <= 0xFF:
        return pl.UInt8
    if max_value <= 0xFFFF:
        return pl.UInt16
    if max_value <= 0xFFFFFFFF:
        return pl.UInt32
    return pl.UInt64


def _max_case_length(df: pl.LazyFrame, case_id_key: str) -> int:
    max_case_length = _scalar_from_lazy(
        df.group_by(case_id_key).agg(pl.len().alias("__case_size")),
        pl.col("__case_size").max(),
    )
    return int(max_case_length or 0)


def automatic_feature_selection_df(
    df: pl.LazyFrame, parameters: Optional[Dict[Any, Any]] = None
) -> pl.LazyFrame:
    """Selects useful features from a Polars lazyframe for ML purposes."""
    if parameters is None:
        parameters = {}

    schema = _lazy_schema(df)
    available_columns = set(schema.names())

    case_id_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME
    )
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY,
        parameters,
        xes_constants.DEFAULT_TIMESTAMP_KEY,
    )
    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
    )

    default_mandatory = available_columns.intersection(
        {case_id_key, activity_key, timestamp_key}
    )
    mandatory_attributes = exec_utils.get_param_value(
        Parameters.MANDATORY_ATTRIBUTES,
        parameters,
        default_mandatory,
    )
    mandatory_set = set(mandatory_attributes)

    min_different_occ_str_attr = exec_utils.get_param_value(
        Parameters.MIN_DIFFERENT_OCC_STR_ATTR, parameters, 5
    )
    max_different_occ_str_attr = exec_utils.get_param_value(
        Parameters.MAX_DIFFERENT_OCC_STR_ATTR, parameters, 50
    )
    consider_all_attributes = exec_utils.get_param_value(
        Parameters.CONSIDER_ALL_ATTRIBUTES, parameters, True
    )

    other_attributes_to_retain = set()

    total_cases = _scalar_from_lazy(df, pl.col(case_id_key).n_unique())
    total_cases = int(total_cases or 0)

    for col, dtype in schema.items():
        if col == case_id_key:
            continue

        cases_with_value = _scalar_from_lazy(
            df.filter(pl.col(col).is_not_null()),
            pl.col(case_id_key).n_unique(),
        )
        cases_with_value = int(cases_with_value or 0)

        if cases_with_value != total_cases and not consider_all_attributes:
            continue

        if _is_numeric_dtype(dtype):
            other_attributes_to_retain.add(col)
        elif _is_string_dtype(dtype):
            unique_val_count = _scalar_from_lazy(
                df.filter(pl.col(col).is_not_null()),
                pl.col(col).n_unique(),
            )
            unique_val_count = int(unique_val_count or 0)
            if (
                min_different_occ_str_attr
                <= unique_val_count
                <= max_different_occ_str_attr
            ):
                other_attributes_to_retain.add(col)

    attributes_to_retain = mandatory_set.union(other_attributes_to_retain)
    selected_columns = [
        col_name for col_name in schema.names() if col_name in attributes_to_retain
    ]

    return df.select(selected_columns)


def select_number_column(
    df: pl.LazyFrame,
    fea_df: pl.LazyFrame,
    col: str,
    case_id_key: str = constants.CASE_CONCEPT_NAME,
    enable_numeric_attribute_statistics: bool = False,
    numeric_attribute_aggregations: Optional[Collection[str]] = None,
) -> pl.LazyFrame:
    """Adds a numeric column to the feature lazyframe."""
    return select_number_columns(
        df,
        fea_df,
        [col],
        case_id_key=case_id_key,
        enable_numeric_attribute_statistics=enable_numeric_attribute_statistics,
        numeric_attribute_aggregations=numeric_attribute_aggregations,
    )


def select_number_columns(
    df: pl.LazyFrame,
    fea_df: pl.LazyFrame,
    columns: List[str],
    case_id_key: str = constants.CASE_CONCEPT_NAME,
    enable_numeric_attribute_statistics: bool = False,
    numeric_attribute_aggregations: Optional[Collection[str]] = None,
) -> pl.LazyFrame:
    """Adds numeric columns to the feature lazyframe in a single grouped pass."""
    if not columns:
        return fea_df

    df_schema = _lazy_schema(df)
    available = set(df_schema.names())

    clean_columns = [
        c
        for c in _dedupe_preserve_order(columns)
        if c != case_id_key and c in available and _is_numeric_dtype(df_schema[c])
    ]
    if not clean_columns:
        return fea_df

    df_cols = set(_lazy_columns(df))
    row_nr_col = _unique_internal_name(df_cols, "__row_nr")

    cols_to_drop: Set[str] = set()
    agg_exprs: List[pl.Expr] = []

    compute_statistics = (
        enable_numeric_attribute_statistics
        or numeric_attribute_aggregations is not None
    )
    if compute_statistics:
        numeric_attribute_aggregations = _normalize_numeric_attribute_aggregations(
            numeric_attribute_aggregations
        )

    for col in clean_columns:
        feature_columns = _get_numeric_feature_columns(
            [col],
            enable_numeric_attribute_statistics,
            numeric_attribute_aggregations,
        )
        cols_to_drop.update([col, f"{col}_right"])
        for feature_col in feature_columns:
            cols_to_drop.update([feature_col, f"{feature_col}_right"])

        feature_dtype = _numeric_feature_dtype(df_schema[col])
        ordered_values = pl.col(col).sort_by(pl.col(row_nr_col)).drop_nulls()

        if compute_statistics and not _is_internal_attribute(col):
            float_values = pl.col(col).cast(pl.Float64)
            aggregation_exprs = {
                "last": ordered_values.last().cast(feature_dtype),
                "first": ordered_values.first().cast(feature_dtype),
                "min": pl.col(col).min().cast(feature_dtype),
                "max": pl.col(col).max().cast(feature_dtype),
                "mean": float_values.mean().cast(pl.Float32),
                "median": float_values.median().cast(pl.Float32),
                "stdev": float_values.std(ddof=0).cast(pl.Float32),
                "sum": (
                    pl.when(pl.col(col).is_not_null().sum() > 0)
                    .then(float_values.sum())
                    .otherwise(None)
                    .cast(pl.Float32)
                ),
            }
            for aggregation in numeric_attribute_aggregations:
                suffix = _NUMERIC_ATTRIBUTE_AGGREGATION_SUFFIXES[aggregation]
                agg_exprs.append(
                    aggregation_exprs[aggregation].alias(f"{col}_{suffix}")
                )
        else:
            agg_exprs.append(
                ordered_values.last().cast(feature_dtype).alias(col)
            )

    fea_df = _drop_if_present(fea_df, cols_to_drop)
    if not agg_exprs:
        return fea_df

    df_numeric = (
        df.with_row_index(row_nr_col)
        .select([pl.col(case_id_key), pl.col(row_nr_col)] + [pl.col(c) for c in clean_columns])
        .group_by(case_id_key)
        .agg(agg_exprs)
    )

    return fea_df.join(df_numeric, on=case_id_key, how="left", coalesce=True, maintain_order="left")


def _collect_categorical_values(
    df: pl.LazyFrame, columns: List[str]
) -> Dict[str, List[Any]]:
    """Collects formatted unique values for the provided categorical columns."""
    collected: Dict[str, List[Any]] = {}
    for col in columns:
        unique_values = (
            df.select(pl.col(col))
            .drop_nulls(subset=[col])
            .unique()
            .collect()
            .get_column(col)
            .to_list()
        )
        formatted = [
            value
            for value in pandas_utils.format_unique(unique_values)
            if value is not None
        ]
        if formatted:
            collected[col] = formatted

    return collected


def _select_string_columns(
    df: pl.LazyFrame,
    fea_df: pl.LazyFrame,
    columns: List[str],
    case_id_key: str,
    count_occurrences: bool,
) -> pl.LazyFrame:
    """Adds one-hot or count encoded columns for the provided categorical attributes.

    This function is designed to be idempotent: running it multiple times with the same
    inputs will overwrite/recompute the same generated feature columns instead of
    creating suffixed duplicates (e.g., `...__1`, `..._right`).
    """
    if not columns:
        return fea_df

    df_schema = _lazy_schema(df)
    available = set(df_schema.names())

    clean_columns = [
        c
        for c in _dedupe_preserve_order(columns)
        if c != case_id_key and c in available
    ]
    if not clean_columns:
        return fea_df

    unique_values_map = _collect_categorical_values(df, clean_columns)
    if not unique_values_map:
        return fea_df

    existing_cols: Set[str] = set(_lazy_columns(fea_df))
    used_names: Set[str] = set(existing_cols)

    agg_exprs: List[pl.Expr] = []
    cols_to_drop: Set[str] = set()
    feature_dtype = (
        _unsigned_count_dtype(_max_case_length(df, case_id_key))
        if count_occurrences
        else pl.UInt8
    )

    for column, unique_values in unique_values_map.items():
        for value in unique_values:
            # Deterministic base name (no dependency on existing columns).
            base_name = _sanitize_feature_name(column, value)

            # If the feature column already exists, we recompute it (drop first),
            # avoiding `*_right` duplicates from joins.
            if base_name in existing_cols:
                cols_to_drop.add(base_name)
                used_names.discard(base_name)
            if f"{base_name}_right" in existing_cols:
                cols_to_drop.add(f"{base_name}_right")
                used_names.discard(f"{base_name}_right")

            # Ensure uniqueness against the remaining schema + other new features.
            column_name = base_name
            suffix = 1
            while column_name in used_names:
                column_name = f"{base_name}__{suffix}"
                suffix += 1
            used_names.add(column_name)

            comparison = pl.col(column).eq(value)
            if count_occurrences:
                agg_exprs.append(
                    comparison.cast(pl.UInt8).sum().cast(feature_dtype).alias(column_name)
                )
            else:
                agg_exprs.append(
                    comparison.cast(feature_dtype).max().cast(feature_dtype).alias(column_name)
                )

    if cols_to_drop:
        fea_df = _drop_if_present(fea_df, cols_to_drop)

    feature_chunk = (
        df.select([pl.col(case_id_key)] + [pl.col(c) for c in unique_values_map.keys()])
        .group_by(case_id_key)
        .agg(agg_exprs)
    )

    return fea_df.join(feature_chunk, on=case_id_key, how="left", coalesce=True, maintain_order="left")


def select_string_column(
    df: pl.LazyFrame,
    fea_df: pl.LazyFrame,
    col: str,
    case_id_key: str = constants.CASE_CONCEPT_NAME,
    count_occurrences: bool = False,
) -> pl.LazyFrame:
    """Adds one-hot or count encoded columns for a categorical attribute."""
    return _select_string_columns(
        df,
        fea_df,
        [col],
        case_id_key=case_id_key,
        count_occurrences=count_occurrences,
    )


def select_string_columns(
    df: pl.LazyFrame,
    fea_df: pl.LazyFrame,
    columns: List[str],
    case_id_key: str = constants.CASE_CONCEPT_NAME,
    count_occurrences: bool = False,
) -> pl.LazyFrame:
    """Adds one-hot or count encoded columns for the provided categorical attributes."""
    return _select_string_columns(
        df,
        fea_df,
        columns,
        case_id_key=case_id_key,
        count_occurrences=count_occurrences,
    )


def get_features_df(
    df: pl.LazyFrame,
    list_columns: List[str],
    parameters: Optional[Dict[Any, Any]] = None,
) -> pl.LazyFrame:
    """Performs automatic feature extraction on a Polars LazyFrame."""
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME
    )
    add_case_identifier_column = exec_utils.get_param_value(
        Parameters.ADD_CASE_IDENTIFIER_COLUMN, parameters, False
    )
    count_occurrences = exec_utils.get_param_value(
        Parameters.COUNT_OCCURRENCES, parameters, False
    )
    enable_numeric_attribute_statistics = exec_utils.get_param_value(
        Parameters.ENABLE_NUMERIC_ATTRIBUTE_STATISTICS, parameters, False
    )
    numeric_attribute_aggregations = exec_utils.get_param_value(
        Parameters.NUMERIC_ATTRIBUTE_AGGREGATIONS, parameters, None
    )

    # Avoid duplicate work and join-induced `*_right` columns when the
    # input list contains duplicates.
    list_columns = _dedupe_preserve_order(list_columns)

    fea_df = df.select(pl.col(case_id_key)).unique().sort(case_id_key, maintain_order=True)

    schema = _lazy_schema(df)
    numeric_columns: List[str] = []
    string_columns: List[str] = []

    for col in list_columns:
        if col == case_id_key or col not in schema:
            continue
        dtype = schema[col]
        if _is_numeric_dtype(dtype):
            numeric_columns.append(col)
        elif _is_string_dtype(dtype):
            string_columns.append(col)

    fea_df = select_number_columns(
        df,
        fea_df,
        numeric_columns,
        case_id_key=case_id_key,
        enable_numeric_attribute_statistics=enable_numeric_attribute_statistics,
        numeric_attribute_aggregations=numeric_attribute_aggregations,
    )

    fea_df = select_string_columns(
        df,
        fea_df,
        string_columns,
        case_id_key=case_id_key,
        count_occurrences=count_occurrences,
    )

    fea_df = fea_df.sort(case_id_key, maintain_order=True)
    if not add_case_identifier_column:
        fea_df = fea_df.drop(case_id_key)

    return fea_df


def automatic_feature_extraction_df(
    df: pl.LazyFrame, parameters: Optional[Dict[Any, Any]] = None
) -> pl.LazyFrame:
    """Wrapper that performs automatic feature extraction on a Polars lazyframe."""
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME
    )
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY,
        parameters,
        xes_constants.DEFAULT_TIMESTAMP_KEY,
    )

    fea_sel_df = automatic_feature_selection_df(df, parameters=parameters)
    columns = set(_lazy_columns(fea_sel_df))

    columns.discard(case_id_key)
    columns.discard(timestamp_key)

    return get_features_df(fea_sel_df, list(columns), parameters=parameters)
