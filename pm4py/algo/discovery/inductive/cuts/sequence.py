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
import itertools
import sys
from abc import ABC
from collections import Counter
from typing import Collection, Any, List, Optional, Generic, Dict
from typing import Tuple

from pm4py.algo.discovery.inductive.cuts.abc import Cut
from pm4py.algo.discovery.inductive.cuts.abc import T
from pm4py.algo.discovery.inductive.dtypes.im_dfg import InductiveDFG
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG
from pm4py.objects.dfg import util as dfu
from pm4py.objects.dfg.obj import DFG
from pm4py.objects.process_tree.obj import Operator, ProcessTree


class SequenceCut(Cut[T], ABC, Generic[T]):

    @classmethod
    def operator(cls, parameters: Optional[Dict[str, Any]] = None) -> ProcessTree:
        return ProcessTree(operator=Operator.SEQUENCE)

    @staticmethod
    def check_merge_condition(g1, g2, trans_succ):
        for a1 in g1:
            for a2 in g2:
                if (a2 in trans_succ[a1] and a1 in trans_succ[a2]) or (a2 not in trans_succ[a1] and a1 not in trans_succ[a2]):
                    return True
        return False

    @staticmethod
    def merge_groups(groups, trans_succ):
        i = 0
        while i < len(groups):
            j = i + 1
            while j < len(groups):
                if SequenceCut.check_merge_condition(groups[i], groups[j], trans_succ):
                    groups[i] = groups[i].union(groups[j])
                    del groups[j]
                    continue
                j = j + 1
            i = i + 1
        return groups

    @classmethod
    def holds(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[List[Collection[Any]]]:
        '''
        This method finds a sequence cut in the dfg.
        Implementation follows function sequence on page 188 of
        "Robust Process Mining with Guarantees" by Sander J.J. Leemans (ISBN: 978-90-386-4257-4)

        Basic Steps:
        1. create a group per activity
        2. merge pairwise reachable nodes (based on transitive relations)
        3. merge pairwise unreachable nodes (based on transitive relations)
        4. sort the groups based on their reachability
        '''
        dfg = obj.dfg
        alphabet = dfu.get_vertices(dfg)
        transitive_predecessors, transitive_successors = dfu.get_transitive_relations(dfg)
        groups = [{a} for a in alphabet]
        if len(groups) == 0:
            return None

        old_size = None
        while old_size != len(groups):
            old_size = len(groups)
            groups = SequenceCut.merge_groups(groups, transitive_successors)

        groups = list(sorted(groups, key=lambda g: len(
            transitive_predecessors[next(iter(g))]) + (len(alphabet) - len(transitive_successors[next(iter(g))]))))

        return groups if len(groups) > 1 else None


class StrictSequenceCut(SequenceCut[T], ABC, Generic[T]):

    @classmethod
    def _skippable(cls, p: int, dfg: DFG, start: Collection[Any], end: Collection[Any],
                   groups: List[Collection[Any]], parameters: Optional[Dict[str, Any]] = None) -> bool:
        """
        This method implements the function SKIPPABLE as defined on page 233 of
        "Robust Process Mining with Guarantees" by Sander J.J. Leemans (ISBN: 978-90-386-4257-4)
        The function is used as a helper function for the strict sequence cut detection mechanism, which detects
        larger groups of skippable activities.
        """
        for i, j in itertools.product(range(0, p), range(p + 1, len(groups))):
            for a, b in itertools.product(groups[i], groups[j]):
                if (a, b) in dfg.graph:
                    return True
        for i in range(p + 1, len(groups)):
            for a in groups[i]:
                if a in start:
                    return True
        for i in range(0, p):
            for a in groups[i]:
                if a in end:
                    return True
        return False

    @classmethod
    def holds(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[List[Collection[Any]]]:
        """
        This method implements the strict sequence cut as defined on page 233 of
        "Robust Process Mining with Guarantees" by Sander J.J. Leemans (ISBN: 978-90-386-4257-4)
        The function merges groups that together can be skipped.
        """
        dfg = obj.dfg
        c = SequenceCut.holds(obj)
        start = set(dfg.start_activities.keys())
        end = set(dfg.end_activities.keys())
        if c is not None:
            mf = [-1 * sys.maxsize if len(set(G).intersection(start)) > 0 else sys.maxsize for G in c]
            mt = [sys.maxsize if len(set(G).intersection(end)) > 0 else -1 * sys.maxsize for G in c]
            cmap = cls._construct_alphabet_cluster_map(c)
            for (a, b) in dfg.graph:
                mf[cmap[b]] = min(mf[cmap[b]], cmap[a])
                mt[cmap[a]] = max(mt[cmap[a]], cmap[b])

            for p in range(0, len(c)):
                if cls._skippable(p, dfg, start, end, c):
                    q = p - 1
                    while q >= 0 and mt[q] <= p:
                        c[p] = c[p].union(c[q])
                        c[q] = set()
                        q -= 1
                    q = p + 1
                    while q < len(mf) and mf[q] >= p:
                        c[p] = c[p].union(c[q])
                        c[q] = set()
                        q += 1
            return list(filter(lambda g: len(g) > 0, c))
        return None

    @classmethod
    def _construct_alphabet_cluster_map(cls, c: List[Collection[Any]], parameters: Optional[Dict[str, Any]] = None):
        map = dict()
        for i in range(0, len(c)):
            for a in c[i]:
                map[a] = i
        return map


class SequenceCutUVCL(SequenceCut[IMDataStructureUVCL]):

    @classmethod
    def project(cls, obj: IMDataStructureUVCL, groups: List[Collection[Any]], parameters: Optional[Dict[str, Any]] = None) -> List[IMDataStructureUVCL]:
        logs = [Counter() for g in groups]
        for t in obj.data_structure:
            i = 0
            split_point = 0
            act_union = set()
            while i < len(groups):
                new_split_point = cls._find_split_point(
                    t, groups[i], split_point, act_union)
                trace_i = tuple()
                j = split_point
                while j < new_split_point:
                    if t[j] in groups[i]:
                        trace_i = trace_i + (t[j],)
                    j = j + 1
                logs[i].update({trace_i: obj.data_structure[t]})
                split_point = new_split_point
                act_union = act_union.union(set(groups[i]))
                i = i + 1
        return list(map(lambda l: IMDataStructureUVCL(l), logs))

    @classmethod
    def _find_split_point(cls, t: Tuple[Any], group: Collection[Any], start: int, ignore: Collection[Any], parameters: Optional[Dict[str, Any]] = None) -> int:
        least_cost = 0
        position_with_least_cost = start
        cost = 0
        i = start
        while i < len(t):
            if t[i] in group:
                cost = cost - 1
            elif t[i] not in ignore:
                cost = cost + 1

            if cost < least_cost:
                least_cost = cost
                position_with_least_cost = i + 1

            i = i + 1

        return position_with_least_cost


class StrictSequenceCutUVCL(StrictSequenceCut[IMDataStructureUVCL], SequenceCutUVCL):

    @classmethod
    def holds(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[List[Collection[Any]]]:
        return StrictSequenceCut.holds(obj, parameters)


class SequenceCutDFG(SequenceCut[IMDataStructureDFG]):

    @classmethod
    def project(cls, obj: IMDataStructureDFG, groups: List[Collection[Any]], parameters: Optional[Dict[str, Any]] = None) -> List[IMDataStructureDFG]:
        dfg = obj.dfg
        start_activities = []
        end_activities = []
        activities = []
        dfgs = []
        skippable = []
        for g in groups:
            skippable.append(False)
        activities_idx = {}
        for gind, g in enumerate(groups):
            for act in g:
                activities_idx[act] = int(gind)
        i = 0
        while i < len(groups):
            to_succ_arcs = Counter()
            from_prev_arcs = Counter()
            if i < len(groups) - 1:
                for (a, b) in dfg.graph:
                    if a in groups[i] and b in groups[i + 1]:
                        to_succ_arcs[a] += dfg.graph[(a, b)]

            if i > 0:
                for (a, b) in dfg.graph:
                    if a in groups[i - 1] and b in groups[i]:
                        from_prev_arcs[b] += dfg.graph[(a, b)]

            if i == 0:
                start_activities.append({})
                for a in dfg.start_activities:
                    if a in groups[i]:
                        start_activities[i][a] = dfg.start_activities[a]
                    else:
                        j = i
                        while j < activities_idx[a]:
                            skippable[j] = True
                            j = j + 1
            else:
                start_activities.append(from_prev_arcs)

            if i == len(groups) - 1:
                end_activities.append({})
                for a in dfg.end_activities:
                    if a in groups[i]:
                        end_activities[i][a] = dfg.end_activities[a]
                    else:
                        j = activities_idx[a] + 1
                        while j <= i:
                            skippable[j] = True
                            j = j + 1
            else:
                end_activities.append(to_succ_arcs)

            activities.append({})
            act_count = dfu.get_vertex_frequencies(dfg)
            for a in groups[i]:
                activities[i][a] = act_count[a]
            dfgs.append({})
            for (a, b) in dfg.graph:
                if a in groups[i] and b in groups[i]:
                    dfgs[i][(a, b)] = dfg.graph[(a, b)]
            i = i + 1
        i = 0
        while i < len(dfgs):
            dfi = DFG()
            [dfi.graph.update({(a, b): dfgs[i][(a, b)]}) for (a, b) in dfgs[i]]
            [dfi.start_activities.update({a: start_activities[i][a]}) for a in start_activities[i]]
            [dfi.end_activities.update({a: end_activities[i][a]}) for a in end_activities[i]]
            dfgs[i] = dfi
            i = i + 1
        for (a, b) in dfg.graph:
            z = activities_idx[b]
            j = activities_idx[a] + 1
            while j < z:
                skippable[j] = False
                j = j + 1

        return [IMDataStructureDFG(InductiveDFG(dfg=dfgs[i], skip=skippable[i])) for i in range(len(dfgs))]


class StrictSequenceCutDFG(StrictSequenceCut[IMDataStructureDFG], SequenceCutDFG):

    @classmethod
    def holds(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[List[Collection[Any]]]:
        return StrictSequenceCut.holds(obj, parameters)
