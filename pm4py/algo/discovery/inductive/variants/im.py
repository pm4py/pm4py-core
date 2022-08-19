from typing import Optional, Tuple, List

from pm4py.algo.discovery.inductive.base_case.empty_log import EmptyLogBaseCase
from pm4py.algo.discovery.inductive.base_case.single_activity import SingleActivityBaseCase
from pm4py.algo.discovery.inductive.cuts.concurrency import ConcurrencyLogCut
from pm4py.algo.discovery.inductive.cuts.loop import LoopLogCut
from pm4py.algo.discovery.inductive.cuts.sequence import StrictSequenceLogCut
from pm4py.algo.discovery.inductive.cuts.xor import ExclusiveChoiceLogCut
from pm4py.algo.discovery.inductive.fall_through.activity_concurrent import ActivityConcurrent
from pm4py.algo.discovery.inductive.fall_through.activity_once_per_trace import ActivityOncePerCase
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTraces
from pm4py.algo.discovery.inductive.fall_through.flower import FlowerModel
from pm4py.algo.discovery.inductive.fall_through.strict_tau_loop import StrictTauLoop
from pm4py.algo.discovery.inductive.fall_through.tau_loop import TauLoop
from pm4py.algo.discovery.inductive.variants.abc import InductiveMinerFramework
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL


class IM(InductiveMinerFramework[UVCL]):

    def fall_through(self, obj: UVCL):
        ft = ActivityOncePerCase.apply(obj)
        ft = ActivityConcurrent.apply(obj) if ft is None else ft
        ft = StrictTauLoop.apply(obj) if ft is None else ft
        ft = TauLoop.apply(obj) if ft is None else ft
        ft = FlowerModel.apply(obj) if ft is None else ft
        return ft

    def apply(self, obj: UVCL) -> ProcessTree:
        empty_traces = EmptyTraces.apply(obj)
        if empty_traces is not None:
            return self._recurse(empty_traces[0], empty_traces[1])
        tree = self.apply_base_case(obj)
        if tree is None:
            cut = self.find_cut(obj)
            if cut is not None:
                tree = self._recurse(cut[0], cut[1])
        if tree is None:
            ft = self.fall_through(obj)
            tree = self._recurse(ft[0], ft[1])
        return tree

    def _recurse(self, tree: ProcessTree, logs: List[UVCL]):
        children = [self.apply(log) for log in logs]
        for c in children:
            c.parent = tree
        tree.children.extend(children)
        return tree

    def apply_base_case(self, obj: UVCL) -> Optional[ProcessTree]:
        bc = EmptyLogBaseCase.apply(obj)
        return bc if bc is not None else SingleActivityBaseCase.apply(obj)

    def find_cut(self, obj: UVCL) -> Optional[Tuple[ProcessTree, List[UVCL]]]:
        dfg = comut.discover_dfg_uvcl(obj)
        g = ExclusiveChoiceLogCut.apply(obj, dfg)
        g = StrictSequenceLogCut.apply(obj, dfg) if g is None else g
        g = ConcurrencyLogCut.apply(obj, dfg) if g is None else g
        return LoopLogCut.apply(obj, dfg) if g is None else g
