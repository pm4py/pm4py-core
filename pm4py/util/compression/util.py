from typing import Union, Tuple, List, Counter
import pandas as pd
from pm4py.objects.log.obj import EventLog
from pm4py.util.compression.dtypes import UCL, MCL, ULT, MLT


def compress_univariate(log: Union[EventLog, pd.DataFrame], key: str = 'concept:name', df_glue: str = 'case:concept:name') -> Tuple[UCL, ULT]:
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
    """
    if type(log) not in {EventLog, pd.DataFrame}:
        raise TypeError('%s provided, expecting %s or %s' %
                        (str(type(log)), str(EventLog), str(pd.DataFrame)))
    vl = [[e[key] for e in t] for t in log] if type(log) is EventLog else [
        log[log[df_glue] == g][key].to_list() for g in frozenset(log[df_glue].to_list())]
    value_map = dict()
    lookup = ULT()
    compressed_log = UCL()
    for t in vl:
        compressed_trace = list()
        for e in t:
            if e not in value_map:
                value_map[e] = len(lookup)
                lookup.append(e)
            compressed_trace.append(value_map[e])
        compressed_log.append(compressed_trace)
    return compressed_log, lookup


def compress_mutlivariate(log: Union[EventLog, pd.DataFrame], keys: List[str] = ['concept:name'], df_glue: str = 'case:concept:name') -> Tuple[MCL, MLT]:
    """
    Compresses an event log to a list of lists containing tupes of integers.
    For example, an event log of the form [[('concept:name':A,'k1':v1,'k2':v2),('concept:name':B,'k1':v3,'k2':v4),...],...]
    is converted to [[(0,0),(1,1),...],...] with corresponding lookup table ['A', 'B'], i.e., if the 'concept:name' and 'k1' columns are used
    for comperssion.

    The method returns a tuple containing the compressed log and the lookup table

    :rtype: ``Tuple[MCL,MLT]``
    :param log: log to compress (either EventLog or Dataframe)
    :param keys: keys to use for compression
    :param df_glue: key to use for combining events into traces when the input is a dataframe.
    """
    if type(log) not in {EventLog, pd.DataFrame}:
        raise TypeError('%s provided, expecting %s or %s' %
                        (str(type(log)), str(EventLog), str(pd.DataFrame)))
    vl = [[tuple([e[k] for k in keys])for e in t] for t in log] if type(log) is EventLog else [
        list(log[log[df_glue] == g][keys].itertuples(index=False)) for g in frozenset(log[df_glue].to_list())]
    value_map = [dict() for k in keys]
    lookup = MLT([] for k in keys)
    compressed_log = MCL()
    for t in vl:
        compressed_trace = []
        for e in t:
            tpl = tuple()
            for i, val in enumerate(e):
                if val not in value_map[i]:
                    value_map[i][val] = len(lookup[i])
                    lookup[i].append(val)
                tpl += (value_map[i][val],)
            compressed_trace.append(tpl)
        compressed_log.append(compressed_trace)
    return compressed_log, lookup


def discover_dfg(log: Union[UCL, MCL], index=0) -> Counter[Tuple[int, int]]:
    """
    Discover a DFG object from a compressed event log (either univariate or multivariate)
    The DFG object represents a counter of integer pairs

    :rtype: ``Counter[Tuple[int, int]]``
    :param log: compressed event log (either uni or multivariate)
    :param indes: index to use for dfg discovery in case of using an multivariate log
    """
    dfg = Counter()
    for t in log:
        for i in range(0, len(t)-1):
            if type(log) is UCL:
                dfg.update([(t[i], t[i+1])])
            elif type(log) is MCL:
                dfg.update([(t[i][index], t[i+1][index])])
    return dfg


def get_start_activities(log: Union[UCL, MCL], index=0):
    return set(map(lambda t: t[0], filter(lambda t: len(t) > 0, log))) if type(log) is UCL else set(map(lambda t: t[0][index], filter(lambda t: len(t) > 0, log)))


def get_end_activities(log: Union[UCL, MCL], index=0):
    return set(map(lambda t: t[len(t)-1], filter(lambda t: len(t) > 0, log))) if type(log) is UCL else set(map(lambda t: t[len(t)-1][index], filter(lambda t: len(t) > 0, log)))


def get_alphabet(log: Union[UCL, MCL], index=0):
    return set([e for t in log for e in t]) if type(log) is UCL else set([e[index] for t in log for e in t])
