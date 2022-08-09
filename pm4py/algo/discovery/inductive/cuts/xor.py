from abc import ABC
from typing import Optional, List, Collection, Any, Tuple, Generic

from pm4py.algo.discovery.inductive.cuts.abc import Cut, T
from pm4py.objects.dfg import util as dfu
from pm4py.objects.dfg.obj import DFG
from pm4py.objects.process_tree.obj import Operator, ProcessTree
from pm4py.util.compression.dtypes import UCL, UCT


class ExclusiveChoiceCut(Cut[T], ABC, Generic[T]):

    @classmethod
    def operator(cls) -> ProcessTree:
        return ProcessTree(operator=Operator.XOR)

    @classmethod
    def holds(cls, obj: T, dfg: DFG = None) -> Optional[List[Collection[Any]]]:
        '''
        This method finds a xor cut in the dfg.
        Implementation follows function XorCut on page 188 of
        "Robust Process Mining with Guarantees" by Sander J.J. Leemans (ISBN: 978-90-386-4257-4)

        Basic Steps:
        1.) the dfg is transformed to its undirected equivalent.
        2.) we detect the connected components in the graph.
        3.) if there are more than one connected components, the cut exists and is non-minimal.
        '''
        import networkx as nx
        nx_dfg = dfu.as_nx_graph(dfg)
        nx_und = nx_dfg.to_undirected()
        conn_comps = [nx_und.subgraph(c).copy() for c in nx.connected_components(nx_und)]
        if len(conn_comps) > 1:
            cuts = list()
            for comp in conn_comps:
                cuts.append(set(comp.nodes))
            return cuts
        else:
            return None


class ExclusiveChoiceLogCut(ExclusiveChoiceCut[UCL]):
    @classmethod
    def project(cls, log: UCL, groups: List[Collection[Any]]) -> List[UCL]:
        logs = [UCL() for g in groups]
        for t in log:
            count = {i: 0 for i in range(len(groups))}
            for index, group in enumerate(groups):
                for e in t:
                    if e in group:
                        count[index] += 1
            count = sorted(list((x, y) for x, y in count.items()), key=lambda x: (x[1], x[0]), reverse=True)
            new_trace = UCT()
            for e in t:
                if e in groups[count[0][0]]:
                    new_trace.append(e)
            logs[count[0][0]].append(new_trace)
        return logs


class ExclusiveChoiceDFGCut(ExclusiveChoiceCut[DFG]):

    @classmethod
    def project(cls, dfg: DFG, groups: List[Collection[Any]]) -> Tuple[List[DFG], List[bool]]:
        dfgs = []
        for g in groups:
            dfg_new = DFG()
            [dfg_new.start_activities.append((a, f)) for (a, f) in dfg.start_activities if a in g]
            [dfg_new.end_activities.append((a, f)) for (a, f) in dfg.end_activities if a in g]
            [dfg_new.graph.append((a, b, f)) for (a, b, f) in dfg.graph if a in g and b in g]
            dfgs.append(dfg)
        return dfgs, [False for g in groups]
