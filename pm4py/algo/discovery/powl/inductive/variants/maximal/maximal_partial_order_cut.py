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
from itertools import combinations
from typing import Any, Optional, Dict, List, Generic, Tuple, Collection

from pm4py.algo.discovery.inductive.cuts.abc import Cut, T
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.objects.powl.BinaryRelation import BinaryRelation
from pm4py.objects.powl.obj import StrictPartialOrder, POWL
from pm4py.objects.dfg import util as dfu
from pm4py.statistics.eventually_follows.uvcl.get import apply as to_efg


def generate_initial_order(nodes, efg):
    po = BinaryRelation(nodes)
    for a, b in combinations(nodes, 2):
        if (a, b) in efg:
            if not (b, a) in efg:
                po.add_edge(a, b)
        else:
            if (b, a) in efg:
                po.add_edge(b, a)
    return po


def remove(blocks, g):
    res = []
    for g2 in blocks:
        if not g2.__str__().__eq__(g.__str__()):
            res.append(g2)
    return res


def contains(blocks, g):
    for g2 in blocks:
        if g2.__str__().__eq__(g.__str__()):
            return True
    return False


def is_valid_order(po, efg, start_activities, end_activities):
    if po is None:
        return False

    if len(po.nodes) < 2:
        return False

    if not po.is_strict_partial_order():
        return False

    start_blocks = po.nodes
    end_blocks = po.nodes

    for group_1, group_2 in combinations(po.nodes, 2):

        edge_g1_g2 = po.is_edge(group_1, group_2)
        edge_g2_g1 = po.is_edge(group_2, group_1)

        if edge_g1_g2:
            start_blocks = remove(start_blocks, group_2)
            end_blocks = remove(end_blocks, group_1)
        if edge_g2_g1:
            start_blocks = remove(start_blocks, group_1)
            end_blocks = remove(end_blocks, group_2)

        all_ef_g1_g2 = True
        all_ef_g2_g1 = True

        for a in group_1:
            for b in group_2:
                if not (a, b) in efg:
                    all_ef_g1_g2 = False
                if not (b, a) in efg:
                    all_ef_g2_g1 = False
        if all_ef_g1_g2 and all_ef_g2_g1 and (edge_g1_g2 or edge_g2_g1):
            return False
        if not edge_g1_g2 and not edge_g2_g1 and not (all_ef_g1_g2 and all_ef_g2_g1):
            return False

    n = len(po.nodes)
    for i in range(n):
        group = po.nodes[i]
        c1 = contains(start_blocks, group)
        c2 = len(set(group).intersection(start_activities)) > 0
        c3 = contains(end_blocks, group)
        c4 = len(set(group).intersection(end_activities)) > 0
        if (c1 and not c2) or (c3 and not c4):
            return False

    return True


def cluster_order(binary_relation):
    pre = {node: set() for node in binary_relation.nodes}
    post = {node: set() for node in binary_relation.nodes}
    for node1 in binary_relation.nodes:
        for node2 in binary_relation.nodes:
            if binary_relation.is_edge(node1, node2):
                pre[node2].add(node1)
                post[node1].add(node2)

    clusters = []
    for node in binary_relation.nodes:
        matched = False
        for i in range(len(clusters)):
            cluster = clusters[i]
            if pre[node] == pre[cluster[0]] and post[node] == post[cluster[0]]:
                clusters[i].append(node)
                matched = True
                break
        if not matched:
            clusters.append([node])

    new_relation = BinaryRelation([tuple(c) for c in clusters])
    for cluster1 in new_relation.nodes:
        for cluster2 in new_relation.nodes:
            node1 = cluster1[0]
            node2 = cluster2[0]
            if binary_relation.is_edge(node1, node2):
                new_relation.add_edge(cluster1, cluster2)

    return new_relation


class MaximalPartialOrderCut(Cut[T], ABC, Generic[T]):

    @classmethod
    def operator(cls, parameters: Optional[Dict[str, Any]] = None) -> StrictPartialOrder:
        raise Exception("This function should not be called!")

    @classmethod
    def holds(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[BinaryRelation]:

        efg = to_efg(obj)
        alphabet = sorted(dfu.get_vertices(obj.dfg), key=lambda g: g.__str__())
        po = generate_initial_order(alphabet, efg)
        clustered_po = cluster_order(po)

        start_activities = set(list(obj.dfg.start_activities.keys()))
        end_activities = set(list(obj.dfg.end_activities.keys()))
        if is_valid_order(clustered_po, efg, start_activities, end_activities):
            return clustered_po
        else:
            return None

    @classmethod
    def apply(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[StrictPartialOrder,
                                                                                          List[POWL]]]:
        g = cls.holds(obj, parameters)
        if g is None:
            return g
        children = cls.project(obj, g.nodes, parameters)
        po = StrictPartialOrder(children)
        for i, j in combinations(range(len(g.nodes)), 2):
            if g.is_edge_id(i, j):
                po.order.add_edge(children[i], children[j])
            elif g.is_edge_id(j, i):
                po.order.add_edge(children[j], children[i])
        return po, po.children


def project_on_groups_with_unique_activities(log: Counter, groups: List[Collection[Any]]):
    r = list()
    for g in groups:
        new_log = Counter()
        for var, freq in log.items():
            new_var = []
            for activity in var:
                if activity in g:
                    new_var.append(activity)
            new_var_tuple = tuple(new_var)
            if new_var_tuple in new_log.keys():
                new_log[new_var_tuple] = new_log[new_var_tuple] + freq
            else:
                new_log[new_var_tuple] = freq
        r.append(new_log)
    return list(map(lambda l: IMDataStructureUVCL(l), r))


class MaximalPartialOrderCutUVCL(MaximalPartialOrderCut[IMDataStructureUVCL]):

    @classmethod
    def project(cls, obj: IMDataStructureUVCL, groups: List[Collection[Any]],
                parameters: Optional[Dict[str, Any]] = None) -> List[IMDataStructureUVCL]:
        return project_on_groups_with_unique_activities(obj.data_structure, groups)
