from multiprocessing import Pool, Manager
from typing import List, TypeVar, Tuple

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure, IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.algo.discovery.inductive.fall_through.activity_concurrent import ActivityConcurrentUVCL
from pm4py.algo.discovery.inductive.fall_through.activity_once_per_trace import ActivityOncePerTraceUVCL
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTracesUVCL
from pm4py.algo.discovery.inductive.fall_through.flower import FlowerModelUVCL, FlowerModelDFG
from pm4py.algo.discovery.inductive.fall_through.strict_tau_loop import StrictTauLoopUVCL
from pm4py.algo.discovery.inductive.fall_through.tau_loop import TauLoopUVCL
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.process_tree.obj import ProcessTree

T = TypeVar('T', bound=IMDataStructure)
S = TypeVar('S', bound=FallThrough)


class FallThroughFactory:

    @classmethod
    def get_fall_throughs(cls, obj: T, inst: IMInstance) -> List[S]:
        if inst is IMInstance.IM:
            if type(obj) is IMDataStructureUVCL:
                return [EmptyTracesUVCL, ActivityOncePerTraceUVCL, ActivityConcurrentUVCL, StrictTauLoopUVCL,
                        TauLoopUVCL, FlowerModelUVCL]
        if inst is IMInstance.IMd:
            return [FlowerModelDFG]
        return list()

    @classmethod
    def fall_through(cls, obj: T, inst: IMInstance, pool: Pool, manager: Manager) -> Tuple[ProcessTree, List[T]]:
        for f in FallThroughFactory.get_fall_throughs(obj, inst):
            r = f.apply(obj, pool, manager)
            if r is not None:
                return r
        return None
