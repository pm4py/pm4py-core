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

from typing import Dict, Tuple

import polars as pl


def get_freq_triples(
    df: pl.LazyFrame,
    activity_key: str = "concept:name",
    case_id_glue: str = "case:concept:name",
    timestamp_key: str = "time:timestamp",
    sort_caseid_required: bool = True,
    sort_timestamp_along_case_id: bool = True,
) -> Dict[Tuple[str, str, str], int]:
    """Compute frequency triples directly on a Polars LazyFrame."""

    if sort_caseid_required:
        if sort_timestamp_along_case_id:
            df = df.sort([case_id_glue, timestamp_key], maintain_order=True)
        else:
            df = df.sort(case_id_glue, maintain_order=True)

    triples = df.with_columns(
        [
            pl.col(activity_key)
            .shift(-1)
            .over(case_id_glue)
            .alias(activity_key + "_2"),
            pl.col(activity_key)
            .shift(-2)
            .over(case_id_glue)
            .alias(activity_key + "_3"),
        ]
    )

    triples = triples.filter(
        pl.col(activity_key + "_2").is_not_null()
        & pl.col(activity_key + "_3").is_not_null()
    )

    grouped = (
        triples.group_by(
            [activity_key, activity_key + "_2", activity_key + "_3"]
        )
        .agg(pl.len().alias("count"))
        .collect()
    )

    return {
        (
            row[activity_key],
            row[activity_key + "_2"],
            row[activity_key + "_3"],
        ): row["count"]
        for row in grouped.iter_rows(named=True)
    }
