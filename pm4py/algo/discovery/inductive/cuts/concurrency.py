from abc import ABC
from itertools import product
from typing import List, Collection, Any, Tuple, Optional, Generic

from pm4py.algo.discovery.inductive.cuts import utils as cut_util
from pm4py.algo.discovery.inductive.cuts.abc import Cut, T
from pm4py.objects.dfg import util as dfu
from pm4py.objects.dfg.obj import DFG
from pm4py.objects.process_tree.obj import Operator, ProcessTree
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UCL


class ConcurrencyCut(Cut[T], ABC, Generic[T]):

    @classmethod
    def operator(cls) -> ProcessTree:
        return ProcessTree(operator=Operator.PARALLEL)

    @classmethod
    def holds(cls, obj: T, dfg: DFG = None) -> Optional[List[Collection[Any]]]:
        dfg = dfg if dfg is not None else obj if type(obj) is DFG else None
        start_activities = {a for (a, f) in dfg.start_activities}
        end_activities = {a for (a, f) in dfg.end_activities}
        alphabet = dfu.get_vertices(dfg)
        msdw = comut.msdw(obj, comut.msd(obj)) if obj is not None and type(obj) is UCL else None
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
            if len(groups[i].intersection(start_activities)) > 0 and len(
                    groups[i].intersection(end_activities)) > 0:
                i += 1
                continue
            group = groups[i]
            del groups[i]
            if i == 0:
                groups[i].update(group)
            else:
                groups[i - 1].update(group)

        return groups if len(groups) > 1 else None


class ConcurrencyLogCut(ConcurrencyCut[UCL]):

    @classmethod
    def project(cls, obj: UCL, groups: List[Collection[Any]]) -> List[UCL]:
        return [[list(filter(lambda e: e in g, t)) for t in obj] for g in groups]


class ConcurrencyDFGCut(ConcurrencyCut[DFG]):

    @classmethod
    def project(cls, obj: DFG, groups: List[Collection[Any]]) -> Tuple[List[DFG], List[bool]]:
        dfgs = []
        skippable = []
        for g in groups:
            dfn = DFG()
            for (a, f) in obj.start_activities:
                if a in g:
                    dfn.start_activities.append((a, f))
            for (a, f) in obj.end_activities:
                if a in g:
                    dfn.end_activities.append((a, f))
            for (a, b, f) in obj.graph:
                if a in g and b in g:
                    dfn.graph.append((a, b, f))
            skippable.append(False)
        return dfgs, skippable
