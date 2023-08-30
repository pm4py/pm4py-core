from multiprocessing import Pool, Manager
from typing import List, TypeVar, Tuple, Optional, Dict, Any, Type

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure, IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.algo.discovery.powl.inductive.fall_through.activity_concurrent import POWLActivityConcurrentUVCL
from pm4py.algo.discovery.powl.inductive.fall_through.activity_once_per_trace import POWLActivityOncePerTraceUVCL
from pm4py.algo.discovery.powl.inductive.fall_through.empty_traces import POWLEmptyTracesUVCL
from pm4py.algo.discovery.powl.inductive.fall_through.flower import POWLFlowerModelUVCL
from pm4py.algo.discovery.powl.inductive.fall_through.strict_tau_loop import POWLStrictTauLoopUVCL
from pm4py.algo.discovery.powl.inductive.fall_through.tau_loop import POWLTauLoopUVCL
from pm4py.objects.powl.obj import POWL

T = TypeVar('T', bound=IMDataStructure)
S = TypeVar('S', bound=FallThrough)


class FallThroughFactory:

    @classmethod
    def get_fall_throughs(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> List[Type[S]]:
        if type(obj) is IMDataStructureUVCL:
            return [POWLEmptyTracesUVCL, POWLActivityOncePerTraceUVCL, POWLActivityConcurrentUVCL,
                    POWLStrictTauLoopUVCL, POWLTauLoopUVCL, POWLFlowerModelUVCL]
        return list()

    @classmethod
    def fall_through(cls, obj: T, pool: Pool, manager: Manager, parameters: Optional[Dict[str, Any]] = None) -> Tuple[POWL, List[T]] | None:
        for f in FallThroughFactory.get_fall_throughs(obj):
            r = f.apply(obj, pool, manager, parameters)
            if r is not None:
                return r
        return None
