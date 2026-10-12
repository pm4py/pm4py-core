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
from collections import Counter
from typing import Union, Tuple, Any, Optional, Counter as TCounter

import numpy as np
import pandas as pd

from pm4py.objects.dfg.obj import DFG
from pm4py.objects.log.obj import EventLog
from pm4py.util.compression.dtypes import UCL, MCL, UVCL


def is_polars_lazyframe(df: Any) -> bool:
    """Return True if the provided dataframe is a Polars LazyFrame."""
    df_type = str(type(df)).lower()
    return "polars" in df_type and "lazyframe" in df_type


def project_univariate(
    log: Union[EventLog, pd.DataFrame],
    key: str = "concept:name",
    df_glue: str = "case:concept:name",
    df_sorting_criterion_key="time:timestamp",
) -> Optional[UCL]:
    """
    Projects an event log to a univariate list of values
    For example, an event log of the form [[('concept:name':A,'k1':v1,'k2':v2),('concept:name':B,'k1':v3,'k2':v4),...],...]
    is converted to [['A','B',...],...]

    The method returns the compressed log

    :rtype: ``UCL``
    :param log: log to compress (either EventLog or Dataframe)
    :param key: key to use for compression
    :param df_glue: key to use for combining events into traces when the input is a dataframe.
    :param df_sorting_criterion_key: key to use as a sorting criterion for traces (typically timestamps)
    """
    if type(log) is EventLog:
        return [[e[key] for e in t] for t in log]
    else:
        if is_polars_lazyframe(log):
            import polars as pl  # type: ignore[import-untyped]

            log = log.select(
                pl.col(df_glue), pl.col(key), pl.col(df_sorting_criterion_key)
            )
            log = log.sort([df_glue, df_sorting_criterion_key], maintain_order=True)

            grouped = (
                log.group_by(df_glue, maintain_order=True)
                .agg(pl.col(key).alias("__acts"))
                .collect()
            )

            return grouped["__acts"].to_list()
        else:
            # Pandas dataframe part
            log = log.loc[:, [key, df_glue, df_sorting_criterion_key]]

            cl = list()
            log = log.sort_values(by=[df_glue, df_sorting_criterion_key])
            values = log[key].to_numpy().tolist()
            distinct_ids, start_indexes, case_sizes = np.unique(
                log[df_glue].to_numpy(), return_index=True, return_counts=True
            )
            for i in range(len(distinct_ids)):
                cl.append(
                    values[start_indexes[i]: start_indexes[i] + case_sizes[i]]
                )
            return cl
    return None


def discover_dfg(log: Union[UCL, MCL], index: int = 0) -> DFG:
    """
    Discover a DFG object from a compressed event log (either univariate or multivariate)
    The DFG object represents a counter of integer pairs

    :rtype: ``Counter[Tuple[int, int]]``
    :param log: compressed event log (either uni or multivariate)
    :param indes: index to use for dfg discovery in case of using an multivariate log
    """
    log = _map_log_to_single_index(log, index)
    dfg = DFG()
    [
        dfg.graph.update([(t[i], t[i + 1])])
        for t in log
        for i in range(0, len(t) - 1)
        if len(t)
    ]
    dfg.start_activities.update(get_start_activities(log, index))
    dfg.end_activities.update(get_end_activities(log, index))
    return dfg


def discover_dfg_uvcl(log: UVCL) -> DFG:
    dfg = DFG()
    [
        dfg.graph.update({(t[i], t[i + 1]): log[t]})
        for t in log
        for i in range(0, len(t) - 1)
        if len(t)
    ]
    for a in get_alphabet(log):
        for t in log:
            if len(t) > 0:
                if t[0] == a:
                    dfg.start_activities.update({a: log[t]})
                if t[len(t) - 1] == a:
                    dfg.end_activities.update({a: log[t]})
    return dfg


def get_start_activities(
    log: Union[UCL, MCL, UVCL], index: int = 0
) -> TCounter[Any]:
    log = _map_log_to_single_index(log, index)
    starts = Counter()
    starts.update(map(lambda t: t[0], filter(lambda t: len(t) > 0, log)))
    return starts


def get_end_activities(
    log: Union[UCL, MCL, UVCL], index: int = 0
) -> TCounter[Any]:
    log = _map_log_to_single_index(log, index)
    ends = Counter()
    ends.update(
        map(lambda t: t[len(t) - 1], filter(lambda t: len(t) > 0, log))
    )
    return ends


def get_alphabet(log: Union[UCL, MCL, UVCL], index: int = 0):
    log = _map_log_to_single_index(log, index)
    sorted_set = sorted(set([e for t in log for e in t]))
    return sorted_set


def get_variants(log: Union[UCL, MCL], index: int = 0) -> UVCL:
    log = _map_log_to_single_index(log, index)
    return Counter(map(lambda t: tuple(t), log))


def _map_log_to_single_index(log: Union[UCL, MCL, UVCL], i: int):
    return (
        [list(map(lambda v: v[i], t)) for t in log]
        if type(log) is MCL
        else log
    )
