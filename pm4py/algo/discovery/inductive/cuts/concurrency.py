from abc import ABC
from collections import Counter
from itertools import product
from typing import List, Collection, Any, Tuple, Optional, Generic

from pm4py.algo.discovery.inductive.cuts import utils as cut_util
from pm4py.algo.discovery.inductive.cuts.abc import Cut, T
from pm4py.objects.dfg import util as dfu
from pm4py.objects.dfg.obj import DFG
from pm4py.objects.process_tree.obj import Operator, ProcessTree
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL


class ConcurrencyCut(Cut[T], ABC, Generic[T]):

    @classmethod
    def operator(cls) -> ProcessTree:
        return ProcessTree(operator=Operator.PARALLEL)

    @classmethod
    def holds(cls, obj: T, dfg: DFG = None) -> Optional[List[Collection[Any]]]:
        dfg = dfg if dfg is not None else obj if type(obj) is DFG else None
        alphabet = dfu.get_vertices(dfg)
        msdw = comut.msdw(obj, comut.msd(obj)) if obj is not None and type(obj) is UVCL else None
        groups = [{a} for a in alphabet]
        if len(groups) == 0:
            return None
        edges = dfu.get_edges(dfg)
        for a, b in product(alphabet, alphabet):
            if (a, b) not in edges or (b, a) not in edges:
                groups = cut_util.merge_groups_based_on_activities(a, b, groups)
            elif msdw is not None:
                if (a in msdw and b in msdw[a]) or (b in msdw and a in msdw[b]):
                    groups = cut_util.merge_groups_based_on_activities(a, b, groups)

        groups = list(sorted(groups, key=lambda g: len(g)))
        i = 0
        while i < len(groups) and len(groups) > 1:
            if len(groups[i].intersection(set(dfg.start_activities.keys()))) > 0 and len(
                    groups[i].intersection(set(dfg.end_activities.keys()))) > 0:
                i += 1
                continue
            group = groups[i]
            del groups[i]
            if i == 0:
                groups[i].update(group)
            else:
                groups[i - 1].update(group)

        return groups if len(groups) > 1 else None


class ConcurrencyLogCut(ConcurrencyCut[UVCL]):

    @classmethod
    def project(cls, obj: UVCL, groups: List[Collection[Any]]) -> List[UVCL]:
        r = list()
        for g in groups:
            c = Counter()
            for t in obj:
                c[tuple(filter(lambda e: e in g, t))] = obj[t]
            r.append(c)
        return r


class ConcurrencyDFGCut(ConcurrencyCut[DFG]):

    @classmethod
    def project(cls, obj: DFG, groups: List[Collection[Any]]) -> Tuple[List[DFG], List[bool]]:
        dfgs = []
        skippable = []
        for g in groups:
            dfn = DFG()
            for a in obj.start_activities:
                if a in g:
                    dfn.start_activities[a] = obj.start_activities[a]
            for a in obj.end_activities:
                if a in g:
                    dfn.end_activities[a] = obj.end_activities[a]
            for (a, b) in obj.graph:
                if a in g and b in g:
                    dfn.graph[(a, b)] = obj[(a, b)]
            skippable.append(False)
        return dfgs, skippable
