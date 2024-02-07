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
from itertools import product
from abc import ABC
from itertools import combinations
from typing import Any, Optional, Dict, List, Generic, Tuple, Collection

from pm4py.algo.discovery.inductive.cuts.abc import Cut, T
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.objects.powl.BinaryRelation import BinaryRelation
from pm4py.objects.powl.obj import StrictPartialOrder, POWL
from pm4py.algo.discovery.inductive.cuts import utils as cut_util
from pm4py.algo.discovery.powl.inductive.variants.maximal.maximal_partial_order_cut import \
    project_on_groups_with_unique_activities
from pm4py.objects.dfg import util as dfu

ORDER_FREQUENCY_RATIO = "order frequency ratio"


def generate_order(obj: T, clusters, order_frequency_ratio):
    # Step 0: if we have one single group containing all activities ---> invoke fall-through.
    if len(clusters) < 2:
        return None

    # Step 1: Generate Order based on the EFG
    po = BinaryRelation([tuple(c) for c in sorted(clusters)])
    efg_freq = compute_efg_frequencies(obj, groups=po.nodes)

    changed = False
    for i in range(len(po.nodes)):
        cluster_1 = po.nodes[i]
        for j in range(i + 1, len(po.nodes)):
            cluster_2 = po.nodes[j]

            sum_freq = efg_freq[(cluster_1, cluster_2)] + efg_freq[(cluster_2, cluster_1)]
            if sum_freq > 0:
                if (float(efg_freq[(cluster_1, cluster_2)]) / sum_freq) >= order_frequency_ratio:
                    po.add_edge(cluster_1, cluster_2)
                if (float(efg_freq[cluster_2, cluster_1]) / sum_freq) >= order_frequency_ratio:
                    po.add_edge(cluster_2, cluster_1)

    # Step 2: Ensure Transitivity and Irreflexivity
    if not po.is_transitive():
        n = len(po.nodes)
        continue_loop = True
        while continue_loop:
            continue_loop = False
            for i, j, k in product(range(n), range(n), range(n)):
                if i != j and j != k and po.edges[i][j] and po.edges[j][k] and not po.is_edge_id(i, k):
                    if efg_freq[(po.nodes[k], po.nodes[i])] + efg_freq[(po.nodes[i], po.nodes[k])] == 0:
                        po.edges[i][k] = True
                        continue_loop = True
                    else:
                        clusters = cut_util.merge_lists_based_on_activities(po.nodes[i][0], po.nodes[k][0], clusters)
                        return generate_order(obj, clusters, order_frequency_ratio)

    if not po.is_irreflexive():
        for i in range(len(po.nodes)):
            cluster_1 = po.nodes[i]
            for j in range(i + 1, len(po.nodes)):
                cluster_2 = po.nodes[j]
                if po.is_edge(cluster_1, cluster_2) and po.is_edge(cluster_2, cluster_1):
                    clusters = cut_util.merge_lists_based_on_activities(cluster_1[0], cluster_2[0], clusters)
                    changed = True

    if changed:
        return generate_order(obj, clusters, order_frequency_ratio)

    # # Step 3: Detect Choice
    for i in range(len(po.nodes)):
        cluster_1 = po.nodes[i]
        for j in range(i + 1, len(po.nodes)):
            cluster_2 = po.nodes[j]
            if not po.is_edge(cluster_1, cluster_2) and not po.is_edge(cluster_2, cluster_1) \
                    and efg_freq[(cluster_1, cluster_2)] == 0 \
                    and efg_freq[(cluster_2, cluster_1)] == 0:
                clusters = cut_util.merge_lists_based_on_activities(cluster_1[0], cluster_2[0], clusters)
                changed = True

    if changed:
        return generate_order(obj, clusters, order_frequency_ratio)

    # Step 4: Cluster nodes sharing the same pre- and post-sets.
    pre = {node: [] for node in po.nodes}
    post = {node: [] for node in po.nodes}
    for i in range(len(po.nodes)):
        cluster_1 = po.nodes[i]
        for j in range(i + 1, len(po.nodes)):
            cluster_2 = po.nodes[j]
            if po.is_edge(cluster_1, cluster_2):
                pre[cluster_2].append(cluster_1)
                post[cluster_1].append(cluster_2)
            elif po.is_edge(cluster_2, cluster_1):
                pre[cluster_1].append(cluster_2)
                post[cluster_2].append(cluster_1)

    for i in range(len(po.nodes)):
        cluster_1 = po.nodes[i]
        for j in range(i + 1, len(po.nodes)):
            cluster_2 = po.nodes[j]
            if pre[cluster_1] == pre[cluster_2] and post[cluster_1] == post[cluster_2]:
                clusters = cut_util.merge_lists_based_on_activities(cluster_1[0], cluster_2[0], clusters)
                changed = True

    if changed and len(clusters) > 1:
        return generate_order(obj, clusters, order_frequency_ratio)
    else:
        return po


def compute_efg_frequencies(interval_log: IMDataStructureUVCL, groups) -> Dict[Tuple[str, str], int]:
    res = {(g1, g2): 0 for g1 in groups for g2 in groups}

    activity_to_cluster = {}
    for cluster in groups:
        for activity in cluster:
            activity_to_cluster[activity] = cluster

    for trace, freq in interval_log.data_structure.items():
        seen_pairs = set()
        for i in range(len(trace)):
            cluster_1 = activity_to_cluster.get(trace[i])
            for j in range(i + 1, len(trace)):
                cluster_2 = activity_to_cluster.get(trace[j])
                pair = (cluster_1, cluster_2)
                if pair not in seen_pairs:
                    res[pair] += freq
                    seen_pairs.add(pair)
    return res


class DynamicClusteringFrequencyPartialOrderCut(Cut[T], ABC, Generic[T]):

    @classmethod
    def operator(cls, parameters: Optional[Dict[str, Any]] = None) -> StrictPartialOrder:
        raise Exception("This function should not be called!")

    @classmethod
    def holds(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[BinaryRelation]:
        alphabet = sorted(dfu.get_vertices(obj.dfg), key=lambda g: g.__str__())
        clusters = [[a] for a in alphabet]

        if ORDER_FREQUENCY_RATIO in parameters.keys():
            order_frequency_ratio = parameters[ORDER_FREQUENCY_RATIO]
            if not (0.5 < order_frequency_ratio <= 1.0):
                raise ValueError("Parameter value of " + ORDER_FREQUENCY_RATIO + "must be in range: 0.5 < value <= 1.0")
        else:
            order_frequency_ratio = 1.0

        po = generate_order(obj, clusters, order_frequency_ratio)
        return po

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


class DynamicClusteringFrequencyPartialOrderCutUVCL(DynamicClusteringFrequencyPartialOrderCut[IMDataStructureUVCL]):

    @classmethod
    def project(cls, obj: IMDataStructureUVCL, groups: List[Collection[Any]],
                parameters: Optional[Dict[str, Any]] = None) -> List[IMDataStructureUVCL]:
        return project_on_groups_with_unique_activities(obj.data_structure, groups)
