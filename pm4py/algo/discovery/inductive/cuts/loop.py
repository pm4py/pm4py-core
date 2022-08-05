import copy
from abc import ABC
from typing import List, Optional, Collection, Any, Tuple, Generic

from pm4py.algo.discovery.inductive.cuts.abc import Cut, T
from pm4py.objects.dfg import util as dfu
from pm4py.objects.dfg.obj import DFG
from pm4py.objects.process_tree.obj import Operator, ProcessTree
from pm4py.util.compression.dtypes import UCL, UCT


class LoopCut(ABC, Generic[T], Cut[T]):

    @classmethod
    def operator(cls) -> ProcessTree:
        return ProcessTree(operator=Operator.LOOP)

    @classmethod
    def applies(cls, obj: T, dfg: DFG = None) -> Optional[List[Collection[Any]]]:
        """
        This method finds a loop cut in the dfg.
        Implementation follows function LoopCut on page 190 of
        "Robust Process Mining with Guarantees" by Sander J.J. Leemans (ISBN: 978-90-386-4257-4)

        Basic Steps:
        1. merge all start and end activities in one group ('do' group)
        2. remove start/end activities from the dfg
        3. detect connected components in (undirected representative) of the reduced graph
        4. check if each component meets the start/end criteria of the loop cut definition (merge with the 'do' group if not)
        5. return the cut if at least two groups remain

        """
        dfg = dfg if dfg is not None else obj if type(obj) is DFG else None
        start_activities = {a for (a, f) in dfg.start_activities}
        end_activities = {a for (a, f) in dfg.end_activities}
        if len(dfg.graph) == 0:
            return None

        groups = [start_activities.union(end_activities)]
        for c in cls._compute_connected_components(dfg, start_activities, end_activities):
            groups.append(set(c.nodes))

        groups = cls._exclude_sets_non_reachable_from_start(dfg, start_activities, end_activities, groups)
        groups = cls._exclude_sets_no_reachable_from_end(dfg, start_activities, end_activities, groups)
        groups = cls._check_start_completeness(dfg, start_activities, end_activities, groups)
        groups = cls._check_end_completeness(dfg, start_activities, end_activities, groups)

        groups = list(filter(lambda g: len(g) > 0, groups))

        return groups if len(groups) > 1 else None

    @classmethod
    def _check_start_completeness(cls, dfg: DFG, start_activities: Collection[Any], end_activities: Collection[Any],
                                  groups: List[Collection[Any]]) -> List[Collection[Any]]:
        i = 1
        while i < len(groups):
            merge = False
            for a in groups[i]:
                if merge:
                    break
                for (x, b, f) in dfg.graph:
                    if x == a and b in start_activities:
                        for s in start_activities:
                            if not (a, s, f) in dfg.graph:
                                merge = True
            if merge:
                groups[0] = set(groups[0]).union(groups[i])
                del groups[i]
                continue
            i = i + 1
        return groups

    @classmethod
    def _check_end_completeness(cls, dfg: DFG, start_activities: Collection[Any], end_activities: Collection[Any],
                                groups: List[Collection[Any]]) -> List[Collection[Any]]:
        i = 1
        while i < len(groups):
            merge = False
            for a in groups[i]:
                if merge:
                    break
                for (b, x, f) in dfg.graph:
                    if x == a and b in end_activities:
                        for e in end_activities:
                            if not (e, a, f) in dfg.graph:
                                merge = True
            if merge:
                groups[0] = set(groups[0]).union(groups[i])
                del groups[i]
                continue
            i = i + 1
        return groups

    @classmethod
    def _exclude_sets_non_reachable_from_start(cls, dfg: DFG, start_activities: Collection[Any],
                                               end_activities: Collection[Any],
                                               groups: List[Collection[Any]]) -> List[Collection[Any]]:
        for a in set(start_activities).difference(set(end_activities)):
            for (x, b, f) in dfg.graph:
                if x == a:
                    group_a, group_b = None, None
                    for group in groups:
                        group_a = group if a in group else group_a
                        group_b = group if b in group else group_b
                    groups = [group for group in groups if group != group_a and group != group_b]
                    # we are always merging on the do-part
                    groups.insert(0, group_a.union(group_b))
        return groups

    @classmethod
    def _exclude_sets_no_reachable_from_end(cls, dfg: DFG, start_activities: Collection[Any],
                                            end_activities: Collection[Any],
                                            groups: List[Collection[Any]]) -> List[Collection[Any]]:
        for b in set(end_activities).difference(start_activities):
            for (a, x, f) in dfg.graph:
                if x == b:
                    group_a, group_b = None, None
                    for group in groups:
                        group_a = group if a in group else group_a
                        group_b = group if b in group else group_b
                    groups = [group for group in groups if group != group_a and group != group_b]
                    groups.insert(0, group_a.union(group_b))
        return groups

    @classmethod
    def _compute_connected_components(cls, dfg: DFG, start_activities: Collection[Any],
                                      end_activities: Collection[Any]):
        import networkx as nx
        reduced_dfg = copy.copy(dfg.graph)
        for (a, b, f) in dfg.graph:
            if a in start_activities or a in end_activities or b in start_activities or b in end_activities:
                reduced_dfg.remove((a, b, f))
        nxd = dfu.as_nx_graph(dfg)
        nxu = nxd.to_undirected()
        return [nxd.subgraph(c).copy() for c in nx.connected_components(nxu)]


class LoopLogCut(LoopCut[UCL]):

    @classmethod
    def project(cls, obj: UCL, groups: List[Collection[Any]]) -> List[UCL]:
        do = groups[0]
        redo = groups[1:]
        redo_activities = [y for x in redo for y in x]
        do_log = UCL()
        redo_logs = [UCL() for i in range(len(redo))]
        for t in obj:
            do_trace = UCT()
            redo_trace = UCT()
            for e in t:
                if e in do:
                    do_trace.append(e)
                    if len(redo_trace) > 0:
                        redo_logs = cls._append_trace_to_redo_log(redo_trace, redo_logs, redo)
                        redo_trace = []
                else:
                    if e in redo_activities:
                        redo_trace.append(e)
                        if len(do_trace) > 0:
                            do_log.append(do_trace)
                            do_trace = []
            if len(redo_trace) > 0:
                redo_logs = cls._append_trace_to_redo_log(redo_trace, redo_logs, redo)
            do_log.append(do_trace)
        logs = [do_log]
        logs.extend(redo_logs)
        return logs

    @classmethod
    def _append_trace_to_redo_log(cls, redo_trace: UCT, redo_logs: List[UCL], redo_groups: List[Collection[Any]]) -> \
            List[UCL]:
        activities = set(x for x in redo_trace)
        inte = [(i, len(activities.intersection(redo_groups[i]))) for i in range(len(redo_groups))]
        inte = sorted(inte, key=lambda x: (x[1], x[0]), reverse=True)
        redo_logs[inte[0][0]].append(redo_trace)
        return redo_logs


class LoopDFGCut(LoopCut[DFG]):

    @classmethod
    def project(cls, dfg: DFG, groups: List[Collection[Any]]) -> Tuple[List[DFG], List[bool]]:
        dfgs = []
        skippable = [False, False]
        start_activities = {a for (a, f) in dfg.start_activities}
        end_activities = {a for (a, f) in dfg.end_activities}
        for gind, g in enumerate(groups):
            dfn = DFG()
            for (a, b, f) in dfg.graph:
                if a in g and b in g:
                    dfn.graph.append((a, b, f))
                if b in start_activities and a in end_activities:
                    skippable[1] = True
            if gind == 0:
                for (a, f) in dfg.start_activities:
                    if a in g:
                        dfn.start_activities.append((a, f))
                    else:
                        skippable[0] = True
                for (a, f) in dfg.end_activities:
                    if a in g:
                        dfn.end_activities.append((a, f))
                    else:
                        skippable[1] = True
            elif gind == 1:
                for a in g:
                    dfn.start_activities.append((a, 1))
                    dfn.end_activities.append((a, 1))
            dfgs.append(dfn)
        return dfgs, skippable
