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
from typing import Optional, Dict, Any, Union

import importlib.util

from pm4py.util import exec_utils, constants, xes_constants, pandas_utils


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


DIFF_INDEX = "@@diff_index"
NEXT_INDEX = "@@next_index"


def apply(df, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[str, int]:
    if parameters is None:
        parameters = {}

    if importlib.util.find_spec("polars") is None:
        raise RuntimeError(
            "Polars LazyFrame provided but 'polars' package is not installed."
        )

    import polars as pl  # type: ignore[import-untyped]

    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
    )
    case_id_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME
    )

    required_columns = {activity_key, case_id_key}
    if hasattr(df, "collect_schema"):
        df_columns = df.collect_schema().names()
    else:
        df_columns = df.columns
    missing_columns = [col for col in required_columns if col not in df_columns]
    if missing_columns:
        raise Exception(
            "The provided Polars LazyFrame does not contain the following required columns: "
            + ", ".join(sorted(missing_columns))
        )

    lf = df.select(list(required_columns))
    lf = pandas_utils.insert_ev_in_tr_index(
        lf,
        case_id=case_id_key,
        column_name=constants.DEFAULT_INDEX_IN_TRACE_KEY,
    )

    lf = lf.sort([case_id_key, constants.DEFAULT_INDEX_IN_TRACE_KEY], maintain_order=True)

    lf = lf.with_columns(
        pl.col(constants.DEFAULT_INDEX_IN_TRACE_KEY)
        .shift(-1)
        .over([case_id_key, activity_key])
        .alias(NEXT_INDEX)
    )

    lf = lf.with_columns(
        (pl.col(NEXT_INDEX) - pl.col(constants.DEFAULT_INDEX_IN_TRACE_KEY) - 1).alias(
            DIFF_INDEX
        )
    )

    lf = lf.filter(pl.col(DIFF_INDEX).is_not_null() & (pl.col(DIFF_INDEX) >= 0))

    result = (
        lf.group_by(activity_key)
        .agg(pl.col(DIFF_INDEX).min().alias(DIFF_INDEX))
        .collect()
    )

    return {
        row[activity_key]: int(row[DIFF_INDEX])
        for row in result.iter_rows(named=True)
    }
