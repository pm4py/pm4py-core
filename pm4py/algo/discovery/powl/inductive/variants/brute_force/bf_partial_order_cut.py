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


def xor(a, b):
    if a and not b:
        return True
    elif not a and b:
        return True
    else:
        return False


def get_partitions_of_size_k(nodes, k=None):
    n = len(nodes)
    if k is not None:
        if k < 1:
            raise ValueError(
                "Can't partition in a negative or zero number of groups"
            )
        elif k > n:
            return

    def set_partitions_helper(l, k):
        length = len(l)
        if k == 1:
            yield [tuple(l)]
        elif length == k:
            yield [tuple([s]) for s in l]
        else:
            e, *M = l
            for p in set_partitions_helper(M, k - 1):
                yield [tuple([e]), *p]
            for p in set_partitions_helper(M, k):
                for i in range(len(p)):
                    yield p[:i] + [tuple([e]) + p[i]] + p[i + 1:]

    if k is None:
        for k in range(1, n + 1):
            yield from set_partitions_helper(nodes, k)
    else:
        yield from set_partitions_helper(nodes, k)


def partition(collection):
    i = len(collection)
    while i > 1:
        for part in get_partitions_of_size_k(collection, i):
            yield part
        i = i - 1
    return


def generate_order(parts, efg):
    nodes = parts
    po = BinaryRelation(nodes)
    for group_1, group_2 in combinations(nodes, 2):
        all_ef_g1_g2 = True
        all_ef_g2_g1 = True
        none_ef_g1_g2 = True
        none_ef_g2_g1 = True
        for a in group_1:
            for b in group_2:
                if (a, b) in efg:
                    none_ef_g1_g2 = False
                else:
                    all_ef_g1_g2 = False

                if (b, a) in efg:
                    none_ef_g2_g1 = False
                else:
                    all_ef_g2_g1 = False

        if all_ef_g1_g2 and none_ef_g2_g1:
            po.add_edge(group_1, group_2)
        elif none_ef_g1_g2 and all_ef_g2_g1:
            po.add_edge(group_2, group_1)

    return po


def is_valid_order(po, dfg_graph, efg):
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
        c2 = len(set(group).intersection(set(dfg_graph.start_activities.keys()))) > 0
        c3 = contains(end_blocks, group)
        c4 = len(set(group).intersection(set(dfg_graph.end_activities.keys()))) > 0
        if (c1 and not c2) or (c3 and not c4):
            return False

    return True


class BruteForcePartialOrderCut(Cut[T], ABC, Generic[T]):

    @classmethod
    def operator(cls, parameters: Optional[Dict[str, Any]] = None) -> StrictPartialOrder:
        raise Exception("This function should not be called!")

    @classmethod
    def holds(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[BinaryRelation]:
        dfg_graph = obj.dfg
        efg = to_efg(obj)
        alphabet = sorted(dfu.get_vertices(dfg_graph), key=lambda g: g.__str__())
        for part in partition(alphabet):
            po = generate_order(part, efg)
            if is_valid_order(po, dfg_graph, efg):
                return po
        return None

    @classmethod
    def apply(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[
            Tuple[StrictPartialOrder, List[POWL]]]:
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


class BruteForcePartialOrderCutUVCL(BruteForcePartialOrderCut[IMDataStructureUVCL]):

    @classmethod
    def project(cls, obj: IMDataStructureUVCL, groups: List[Collection[Any]],
                parameters: Optional[Dict[str, Any]] = None) -> List[IMDataStructureUVCL]:
        r = list()
        for g in groups:
            c = Counter()
            for t in obj.data_structure:
                c[tuple(filter(lambda e: e in g, t))] = obj.data_structure[t]
            r.append(c)
        return list(map(lambda l: IMDataStructureUVCL(l), r))
