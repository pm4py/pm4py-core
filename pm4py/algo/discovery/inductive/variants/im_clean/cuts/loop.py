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
from typing import List, Optional, Set, Dict

import networkx as nx
from networkx.classes.graph import Graph

from pm4py.algo.discovery.inductive.variants.im_clean import utils as im_utils
from pm4py.algo.discovery.inductive.variants.im_clean.d_types import Cut, DFG
from pm4py.objects.log.obj import EventLog, Trace


def detect(dfg: DFG, alphabet: Dict[str, int], start_activities: Dict[str, int],
           end_activities: Dict[str, int]) -> Optional[Cut]:
    '''
    This method finds a loop cut in the dfg.
    Implementation follows function LoopCut on page 190 of
    "Robust Process Mining with Guarantees" by Sander J.J. Leemans (ISBN: 978-90-386-4257-4)

    Basic Steps:
    1. merge all start and end activities in one group ('do' group)
    2. remove start/end activities from the dfg
    3. detect connected components in (undirected representative) of the reduced graph
    4. check if each component meets the start/end criteria of the loop cut definition (merge with the 'do' group if not)
    5. return the cut if at least two groups remain

    Parameters
    ----------
    dfg
        directly follows graph
    alphabet
        alphabet of the dfg / log
    start_activities
        multiset of start activities of the dfg / log
    end_activities
        multiset of end activities of the dfg / log

    Returns
    -------
        A list of sets of activities, i.e., forming a maximal loop cut
        None if no cut is found.

    '''
    if len(dfg) == 0:
        return None

    groups = [set(start_activities.keys()).union(set(end_activities.keys()))]
    for c in _compute_connected_components(dfg, alphabet, start_activities, end_activities, groups[0]):
        groups.append(set(c.nodes))

    groups = _exclude_sets_non_reachable_from_start(dfg, start_activities, end_activities, groups)
    groups = _exclude_sets_no_reachable_from_end(dfg, start_activities, end_activities, groups)
    groups = _check_start_completeness(dfg, start_activities, end_activities, groups)
    groups = _check_end_completeness(dfg, start_activities, end_activities, groups)

    groups = list(filter(lambda g: len(g) > 0, groups))

    return groups if len(groups) > 1 else None


def _check_start_completeness(dfg, start_activities, end_activities, groups):
    i = 1
    while i < len(groups):
        merge = False
        for a in groups[i]:
            if merge:
                break
            for (x, b) in dfg:
                if x == a and b in start_activities:
                    for s in start_activities:
                        if not (a, s) in dfg:
                            merge = True
        if merge:
            groups[0] = groups[0].union(groups[i])
            del groups[i]
            continue
        i = i + 1
    return groups


def _check_end_completeness(dfg, start_activities, end_activities, groups):
    i = 1
    while i < len(groups):
        merge = False
        for a in groups[i]:
            if merge:
                break
            for (b, x) in dfg:
                if x == a and b in end_activities:
                    for e in end_activities:
                        if not (e, a) in dfg:
                            merge = True
        if merge:
            groups[0] = groups[0].union(groups[i])
            del groups[i]
            continue
        i = i + 1
    return groups


def _exclude_sets_non_reachable_from_start(dfg: DFG, start_activities: Dict[str, int], end_activities: Dict[str, int],
                                           groups: Cut) -> Cut:
    for a in set(start_activities).difference(set(end_activities)):
        for (x, b) in dfg:
            if x == a:
                group_a, group_b = None, None
                for group in groups:
                    group_a = group if a in group else group_a
                    group_b = group if b in group else group_b
                groups = [group for group in groups if group != group_a and group != group_b]
                # we are always merging on the do-part
                groups.insert(0, group_a.union(group_b))
    return groups


def _exclude_sets_no_reachable_from_end(dfg: DFG, start_activities: Dict[str, int], end_activities: Dict[str, int],
                                        groups: Cut) -> Cut:
    for b in set(end_activities).difference(set(start_activities)):
        for (a, x) in dfg:
            if x == b:
                group_a, group_b = None, None
                for group in groups:
                    group_a = group if a in group else group_a
                    group_b = group if b in group else group_b
                groups = [group for group in groups if group != group_a and group != group_b]
                groups.insert(0, group_a.union(group_b))
    return groups


def _compute_connected_components(dfg: DFG, alphabet: Set[str], start_activities: Dict[str, int],
                                  end_activities: Dict[str, int], do_set: Set[str]) -> List[Graph]:
    reduced_dfg = copy.copy(dfg)
    for (a, b) in dfg:
        if a in end_activities or a in end_activities or b in start_activities or b in end_activities:
            del reduced_dfg[(a, b)]
    reduced_alphabet = set(alphabet).difference(do_set)
    nx_directed = im_utils.transform_dfg_to_directed_nx_graph(reduced_dfg, reduced_alphabet)
    nx_undirected = nx_directed.to_undirected()
    return [nx_undirected.subgraph(c).copy() for c in nx.connected_components(nx_undirected)]


def project(log: EventLog, cut: Cut, activity_key: str) -> List[EventLog]:
    do = cut[0]
    redo = cut[1:]
    redo_activities = [y for x in redo for y in x]
    do_log = EventLog()
    redo_logs = []
    for i in range(len(redo)):
        redo_logs.append(EventLog())
    for t in log:
        do_trace = Trace()
        redo_trace = Trace()
        for e in t:
            if e[activity_key] in do:
                do_trace.append(e)
                if len(redo_trace) > 0:
                    redo_logs = _append_trace_to_redo_log(redo_trace, redo_logs, redo, activity_key)
                    redo_trace = Trace()
            else:
                if e[activity_key] in redo_activities:
                    redo_trace.append(e)
                    if len(do_trace) > 0:
                        do_log.append(do_trace)
                        do_trace = Trace()
        if len(redo_trace) > 0:
            redo_logs = _append_trace_to_redo_log(redo_trace, redo_logs, redo, activity_key)
        do_log.append(do_trace)
    logs = [do_log]
    logs.extend(redo_logs)
    return logs


def _append_trace_to_redo_log(redo_trace: Trace, redo_logs: List[List[Trace]], redo_groups: List[Set[str]],
                              activity_key: str) -> List[List[Trace]]:
    activities = set(x[activity_key] for x in redo_trace)
    inte = [(i, len(activities.intersection(redo_groups[i]))) for i in range(len(redo_groups))]
    inte = sorted(inte, key=lambda x: (x[1], x[0]), reverse=True)
    redo_logs[inte[0][0]].append(redo_trace)
    return redo_logs
