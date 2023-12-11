'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
import copy
from collections import Counter
from typing import Union, Tuple, List, Any, Dict, Optional, Counter as TCounter

import numpy as np
import pandas as pd

from pm4py.objects.dfg.obj import DFG
from pm4py.objects.log.obj import EventLog
from pm4py.util.compression.dtypes import UCL, MCL, ULT, MLT, UVCL
from pm4py.util import pandas_utils


def project_univariate(log: Union[EventLog, pd.DataFrame], key: str = 'concept:name',
                       df_glue: str = 'case:concept:name', df_sorting_criterion_key='time:timestamp') -> Optional[UCL]:
    '''
    Projects an event log to a univariate list of values
    For example, an event log of the form [[('concept:name':A,'k1':v1,'k2':v2),('concept:name':B,'k1':v3,'k2':v4),...],...]
    is converted to [['A','B',...],...] 

    The method returns the compressed log

    :rtype: ``UCL``
    :param log: log to compress (either EventLog or Dataframe)
    :param key: key to use for compression
    :param df_glue: key to use for combining events into traces when the input is a dataframe.
    :param df_sorting_criterion_key: key to use as a sorting criterion for traces (typically timestamps)
    '''
    if type(log) is EventLog:
        return [[e[key] for e in t] for t in log]
    else:
        log = log.loc[:, [key, df_glue, df_sorting_criterion_key]]

        cl = list()
        log = log.sort_values(by=[df_glue, df_sorting_criterion_key])
        values = log[key].to_numpy().tolist()
        distinct_ids, start_indexes, case_sizes = np.unique(
            log[df_glue].to_numpy(), return_index=True, return_counts=True)
        for i in range(len(distinct_ids)):
            cl.append(
                values[start_indexes[i]:start_indexes[i] + case_sizes[i]])
        return cl
    return None


def compress_univariate(log: Union[EventLog, pd.DataFrame], key: str = 'concept:name',
                        df_glue: str = 'case:concept:name',
                        df_sorting_criterion_key='time:timestamp') -> Optional[Tuple[UCL, ULT]]:
    """
    Compresses an event log to a univariate list of integer lists
    For example, an event log of the form [[('concept:name':A,'k1':v1,'k2':v2),('concept:name':B,'k1':v3,'k2':v4),...],...]
    is converted to [[0,1,...],...] with corresponding lookup table ['A', 'B'], i.e., if the 'concept:name' column is used
    for comperssion.

    The method returns a tuple containing the compressed log and the lookup table

    :rtype: ``Tuple[UCL,ULT]``
    :param log: log to compress (either EventLog or Dataframe)
    :param key: key to use for compression
    :param df_glue: key to use for combining events into traces when the input is a dataframe.
    :param df_sorting_criterion_key: key to use as a sorting criterion for traces (typically timestamps)
    """
    if pandas_utils.check_is_pandas_dataframe(log):
        log = log.loc[:, [key, df_glue, df_sorting_criterion_key]]
    lookup = list(set([x for xs in [[e[key] for e in t] for t in log]
                       for x in xs])) if type(log) is EventLog else pandas_utils.format_unique(log[key].unique())
    lookup_inv = {lookup[i]: i for i in range(len(lookup))}
    if type(log) is EventLog:
        return [[lookup_inv[t[i][key]] for i in range(0, len(t))] for t in log], lookup
    else:
        log[key] = log[key].map(lookup_inv)
        cl = list()
        log = log.sort_values(by=[df_glue, df_sorting_criterion_key])
        encoded_values = log[key].to_numpy().tolist()
        distinct_ids, start_indexes, case_sizes = np.unique(
            log[df_glue].to_numpy(), return_index=True, return_counts=True)
        for i in range(len(distinct_ids)):
            cl.append(encoded_values[start_indexes[i]
                                     :start_indexes[i] + case_sizes[i]])
        return cl, lookup
    return None, None


def compress_multivariate(log: Union[EventLog, pd.DataFrame], keys: List[str] = ['concept:name'],
                          df_glue: str = 'case:concept:name',
                          df_sorting_criterion_key: str = 'time:timestamp', uncompressed: List[str] = []) -> Tuple[
    MCL, MLT]:
    """
    Compresses an event log to a list of lists containing tupes of integers.
    For example, an event log of the form [[('concept:name':A,'k1':v1,'k2':v2),('concept:name':B,'k1':v3,'k2':v4),...],...]
    is converted to [[(0,0),(1,1),...],...] with corresponding lookup table ['A', 'B'], i.e., if the 'concept:name' and 'k1' columns are used
    for comperssion.
    The 2nd order criterion is used to sort the values that have the same trace attribute.
    The uncompressed arguments will be included, yet, not compressed (e.g., a boolean value needs not to be compressed)

    The method returns a tuple containing the compressed log and the lookup table. The order of the data in the compressed log follows the ordering of the provided keys. First the compressed columns are stored, secondly the uncompressed columns

    :rtype: ``Tuple[MCL,MLT]``
    :param log: log to compress (either EventLog or Dataframe)
    :param keys: keys to use for compression
    :param df_glue: key to use for combining events into traces when the input is a dataframe.
    :param df_sorting_criterion_key: key to use as a sorting criterion for traces (typically timestamps)
    :param uncompressed: columns that need to be included in the compression yet need not to be compressed

    """
    if pandas_utils.check_is_pandas_dataframe(log):
        retain = copy.copy(keys)
        if df_glue not in retain:
            retain.append(df_glue)
        if df_sorting_criterion_key not in retain:
            retain.append(df_sorting_criterion_key)
        retain.extend([u for u in uncompressed if u not in retain])
        log = log.loc[:, retain]
    lookup = dict()
    lookup_inv = dict()
    for key in keys:
        if key not in uncompressed:
            lookup[key] = list(set([x for xs in [[e[key] for e in t] for t in log]
                                    for x in xs])) if type(log) is EventLog else pandas_utils.format_unique(log[key].unique())
            lookup_inv[key] = {lookup[key][i]: i for i in range(len(lookup[key]))}
    if type(log) is EventLog:
        encoded = list()
        for t in log:
            tr = list()
            for i in range(0, len(t)):
                vec = []
                for key in keys:
                    vec.append(lookup_inv[key][t[i][key]])
                for key in uncompressed:
                    vec.append(t[i][key])
                tr.append(tuple(vec))
            encoded.append(tr)
        return encoded, lookup
    else:
        for key in keys:
            log[key] = log[key].map(lookup_inv[key])
        cl = list()
        log = log.sort_values(by=[df_glue, df_sorting_criterion_key])
        retain = copy.copy(keys)
        retain.extend([u for u in uncompressed if u not in retain])
        encoded_values = list(log[retain].itertuples(index=False, name=None))
        distinct_ids, start_indexes, case_sizes = np.unique(
            log[df_glue].to_numpy(), return_index=True, return_counts=True)
        for i in range(len(distinct_ids)):
            cl.append(encoded_values[start_indexes[i]
                                     :start_indexes[i] + case_sizes[i]])
    return cl, lookup


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
    [dfg.graph.update([(t[i], t[i + 1])]) for t in log for i in range(0, len(t) - 1) if len(t)]
    dfg.start_activities.update(get_start_activities(log, index))
    dfg.end_activities.update(get_end_activities(log, index))
    return dfg


def discover_dfg_uvcl(log: UVCL) -> DFG:
    dfg = DFG()
    [dfg.graph.update({(t[i], t[i + 1]): log[t]}) for t in log for i in range(0, len(t) - 1) if len(t)]
    for a in get_alphabet(log):
        for t in log:
            if len(t) > 0:
                if t[0] == a:
                    dfg.start_activities.update({a: log[t]})
                if t[len(t) - 1] == a:
                    dfg.end_activities.update({a: log[t]})
    return dfg


def get_start_activities(log: Union[UCL, MCL, UVCL], index: int = 0) -> TCounter[Any]:
    log = _map_log_to_single_index(log, index)
    starts = Counter()
    starts.update(map(lambda t: t[0], filter(lambda t: len(t) > 0, log)))
    return starts


def get_end_activities(log: Union[UCL, MCL, UVCL], index: int = 0) -> TCounter[Any]:
    log = _map_log_to_single_index(log, index)
    ends = Counter()
    ends.update(map(lambda t: t[len(t) - 1], filter(lambda t: len(t) > 0, log)))
    return ends


def get_alphabet(log: Union[UCL, MCL, UVCL], index: int = 0):
    log = _map_log_to_single_index(log, index)
    sorted_set = sorted(set([e for t in log for e in t]))
    return sorted_set


def get_variants(log: Union[UCL, MCL], index: int = 0) -> UVCL:
    log = _map_log_to_single_index(log, index)
    return Counter(map(lambda t: tuple(t), log))


def _map_log_to_single_index(log: Union[UCL, MCL, UVCL], i: int):
    return [list(map(lambda v: v[i], t)) for t in log] if type(log) is MCL else log


def msd(ucl: Union[UCL, UVCL]) -> Dict[Any, int]:
    msd = dict()
    for a in get_alphabet(ucl):
        activity_indices = list(
            filter(lambda t: len(t) > 1, map(lambda t: [i for i, x in enumerate(t) if x == a], ucl)))
        if len(activity_indices) > 0:
            msd[a] = min([i for l in map(lambda t: [
                t[i - 1] - t[i] - 1 for i in range(len(t)) if i > 0], activity_indices) for i in l])
    return msd


def msdw(cl: Union[UCL, UVCL], msd: Dict[Any, int]) -> Dict[Any, Any]:
    witnesses = dict()
    alphabet = get_alphabet(cl)
    for a in alphabet:
        if a in msd and msd[a] > 0:
            witnesses[a] = set()
        else:
            continue
        for t in cl:
            if len(list(filter(lambda e: e == a, t))) > 1:
                indices = [i for i, x in enumerate(t) if x == a]
                for i in range(len(indices) - 1):
                    if indices[i + 1] - indices[i] - 1 == msd[a]:
                        for b in t[indices[i] + 1:indices[i + 1]]:
                            witnesses[a].add(b)
    return witnesses
