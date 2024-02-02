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
from abc import ABC
from collections import Counter
from typing import List, Optional, Collection, Any, Tuple, Generic, Dict

from pm4py.util import nx_utils

from pm4py.algo.discovery.inductive.cuts.abc import Cut, T
from pm4py.algo.discovery.inductive.dtypes.im_dfg import InductiveDFG
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG
from pm4py.objects.dfg import util as dfu
from pm4py.objects.dfg.obj import DFG
from pm4py.objects.process_tree.obj import Operator, ProcessTree
from pm4py.util.compression.dtypes import UVCL


class LoopCut(Cut[T], ABC, Generic[T]):

    @classmethod
    def operator(cls, parameters: Optional[Dict[str, Any]] = None) -> ProcessTree:
        return ProcessTree(operator=Operator.LOOP)

    @classmethod
    def holds(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[List[Collection[Any]]]:
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
        dfg = obj.dfg
        start_activities = set(dfg.start_activities.keys())
        end_activities = set(dfg.end_activities.keys())
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
                                  groups: List[Collection[Any]], parameters: Optional[Dict[str, Any]] = None) -> List[Collection[Any]]:
        i = 1
        while i < len(groups):
            merge = False
            for a in groups[i]:
                if merge:
                    break
                for (x, b) in dfg.graph:
                    if x == a and b in start_activities:
                        for s in start_activities:
                            if not (a, s) in dfg.graph:
                                merge = True
            if merge:
                groups[0] = set(groups[0]).union(groups[i])
                del groups[i]
                continue
            i = i + 1
        return groups

    @classmethod
    def _check_end_completeness(cls, dfg: DFG, start_activities: Collection[Any], end_activities: Collection[Any],
                                groups: List[Collection[Any]], parameters: Optional[Dict[str, Any]] = None) -> List[Collection[Any]]:
        i = 1
        while i < len(groups):
            merge = False
            for a in groups[i]:
                if merge:
                    break
                for (b, x) in dfg.graph:
                    if x == a and b in end_activities:
                        for e in end_activities:
                            if not (e, a) in dfg.graph:
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
                                               groups: List[Collection[Any]], parameters: Optional[Dict[str, Any]] = None) -> List[Collection[Any]]:
        for a in set(start_activities).difference(set(end_activities)):
            for (x, b) in dfg.graph:
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
                                            groups: List[Collection[Any]], parameters: Optional[Dict[str, Any]] = None) -> List[Collection[Any]]:
        for b in set(end_activities).difference(start_activities):
            for (a, x) in dfg.graph:
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
                                      end_activities: Collection[Any], parameters: Optional[Dict[str, Any]] = None):
        nxd = dfu.as_nx_graph(dfg)
        [nxd.remove_edge(a, b) for (a, b) in dfg.graph if
         a in start_activities or a in end_activities or b in start_activities or b in end_activities]
        [nxd.remove_node(a) for a in start_activities if nxd.has_node(a)]
        [nxd.remove_node(a) for a in end_activities if nxd.has_node(a)]
        nxu = nxd.to_undirected()
        return [nxd.subgraph(c).copy() for c in nx_utils.connected_components(nxu)]


class LoopCutUVCL(LoopCut[IMDataStructureUVCL]):

    @classmethod
    def project(cls, obj: IMDataStructureUVCL, groups: List[Collection[Any]], parameters: Optional[Dict[str, Any]] = None) -> List[IMDataStructureUVCL]:
        do = groups[0]
        redo = groups[1:]
        redo_activities = [y for x in redo for y in x]
        do_log = Counter()
        redo_logs = [Counter() for i in range(len(redo))]
        for t in obj.data_structure:
            do_trace = tuple()
            redo_trace = tuple()
            for e in t:
                if e in do:
                    do_trace = do_trace + (e,)
                    if len(redo_trace) > 0:
                        redo_logs = cls._append_trace_to_redo_log(redo_trace, redo_logs, redo, obj.data_structure[t])
                        redo_trace = tuple()
                else:
                    if e in redo_activities:
                        redo_trace = redo_trace + (e,)
                        if len(do_trace) > 0:
                            do_log.update({do_trace: obj.data_structure[t]})
                            do_trace = tuple()
            if len(redo_trace) > 0:
                redo_logs = cls._append_trace_to_redo_log(redo_trace, redo_logs, redo)
            do_log.update({do_trace: obj.data_structure[t]})
        logs = [do_log]
        logs.extend(redo_logs)
        return list(map(lambda l: IMDataStructureUVCL(l), logs))

    @classmethod
    def _append_trace_to_redo_log(cls, redo_trace: Tuple, redo_logs: List[UVCL], redo_groups: List[Collection[Any]],
                                  cardinality, parameters: Optional[Dict[str, Any]] = None) -> \
            List[UVCL]:
        activities = set(x for x in redo_trace)
        inte = [(i, len(activities.intersection(redo_groups[i]))) for i in range(len(redo_groups))]
        inte = sorted(inte, key=lambda x: (x[1], x[0]), reverse=True)
        redo_logs[inte[0][0]].update({redo_trace: cardinality})
        return redo_logs


class LoopCutDFG(LoopCut[IMDataStructureDFG]):

    @classmethod
    def project(cls, obj: IMDataStructureUVCL, groups: List[Collection[Any]], parameters: Optional[Dict[str, Any]] = None) -> List[IMDataStructureDFG]:
        dfg = obj.dfg
        dfgs = []
        skippable = [False, False]
        for gind, g in enumerate(groups):
            dfn = DFG()
            for (a, b) in dfg.graph:
                if a in g and b in g:
                    dfn.graph[(a, b)] = dfg.graph[(a, b)]
                if b in dfg.start_activities and a in dfg.end_activities:
                    skippable[1] = True
            if gind == 0:
                for a in dfg.start_activities:
                    if a in g:
                        dfn.start_activities[a] = dfg.start_activities[a]
                    else:
                        skippable[0] = True
                for a in dfg.end_activities:
                    if a in g:
                        dfn.end_activities[a] = dfg.end_activities[a]
                    else:
                        skippable[1] = True
            elif gind == 1:
                for a in g:
                    dfn.start_activities[a] = 1
                    dfn.end_activities[a] = 1
            dfgs.append(dfn)
        return [IMDataStructureDFG(InductiveDFG(dfg=dfgs[i], skip=skippable[i])) for i in range(len(dfgs))]
