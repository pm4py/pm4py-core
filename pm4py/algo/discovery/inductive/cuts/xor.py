from abc import ABC
from collections import Counter
from typing import Optional, List, Collection, Any, Generic

import networkx as nx

from pm4py.algo.discovery.inductive.cuts.abc import Cut, T
from pm4py.algo.discovery.inductive.dtypes.im_dfg import InductiveDFG
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG
from pm4py.objects.dfg import util as dfu
from pm4py.objects.dfg.obj import DFG
from pm4py.objects.process_tree.obj import Operator, ProcessTree


class ExclusiveChoiceCut(Cut[T], ABC, Generic[T]):

    @classmethod
    def operator(cls) -> ProcessTree:
        return ProcessTree(operator=Operator.XOR)

    @classmethod
    def holds(cls, obj: T) -> Optional[List[Collection[Any]]]:
        '''
        This method finds a xor cut in the dfg.
        Implementation follows function XorCut on page 188 of
        "Robust Process Mining with Guarantees" by Sander J.J. Leemans (ISBN: 978-90-386-4257-4)

        Basic Steps:
        1.) the dfg is transformed to its undirected equivalent.
        2.) we detect the connected components in the graph.
        3.) if there are more than one connected components, the cut exists and is non-minimal.
        '''
        nx_dfg = dfu.as_nx_graph(obj.dfg)
        nx_und = nx_dfg.to_undirected()
        conn_comps = [nx_und.subgraph(c).copy() for c in nx.connected_components(nx_und)]
        if len(conn_comps) > 1:
            cuts = list()
            for comp in conn_comps:
                cuts.append(set(comp.nodes))
            return cuts
        else:
            return None


class ExclusiveChoiceCutUVCL(ExclusiveChoiceCut[IMDataStructureUVCL]):
    @classmethod
    def project(cls, obj: IMDataStructureUVCL, groups: List[Collection[Any]]) -> List[IMDataStructureUVCL]:
        logs = [Counter() for g in groups]
        for t in obj.data_structure:
            count = {i: 0 for i in range(len(groups))}
            for index, group in enumerate(groups):
                for e in t:
                    if e in group:
                        count[index] += 1
            count = sorted(list((x, y) for x, y in count.items()), key=lambda x: (x[1], x[0]), reverse=True)
            new_trace = tuple()
            for e in t:
                if e in groups[count[0][0]]:
                    new_trace = new_trace + (e,)
            logs[count[0][0]].update({new_trace: obj.data_structure[t]})
        return list(map(lambda l: IMDataStructureUVCL(l), logs))


class ExclusiveChoiceCutDFG(ExclusiveChoiceCut[IMDataStructureDFG]):

    @classmethod
    def project(cls, dfg: DFG, groups: List[Collection[Any]]) -> List[IMDataStructureDFG]:
        dfgs = []
        for g in groups:
            dfg_new = DFG()
            for a in dfg.start_activities:
                if a in g:
                    dfg_new.start_activities[a] = dfg.start_activities[a]
            for a in dfg.end_activities:
                if a in g:
                    dfg_new.end_activities[a] = dfg.end_activities[a]
            for (a, b) in dfg.graph:
                if a in g and b in g:
                    dfg_new.graph[(a, b)] = dfg.graph[(a, b)]
            dfgs.append(dfg)
        return list(map(lambda d: IMDataStructureDFG(InductiveDFG(dfg=d, skip=False)), dfgs))
