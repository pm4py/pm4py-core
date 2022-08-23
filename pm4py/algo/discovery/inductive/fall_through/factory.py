from typing import List

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure, IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.algo.discovery.inductive.fall_through.activity_concurrent import ActivityConcurrentUVCL
from pm4py.algo.discovery.inductive.fall_through.activity_once_per_trace import ActivityOncePerTraceUVCL
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTracesUVCL
from pm4py.algo.discovery.inductive.fall_through.flower import FlowerModelUVCL
from pm4py.algo.discovery.inductive.fall_through.strict_tau_loop import StrictTauLoopUVCL
from pm4py.algo.discovery.inductive.fall_through.tau_loop import TauLoopUVCL
from pm4py.algo.discovery.inductive.variants.instances import IMInstance


class FallThroughFactory:

    @classmethod
    def get_fall_throughs(cls, obj: IMDataStructure, inst: IMInstance) -> List[FallThrough]:
        if inst is IMInstance.IM:
            if type(obj) is IMDataStructureUVCL:
                return [EmptyTracesUVCL, ActivityOncePerTraceUVCL, ActivityConcurrentUVCL, StrictTauLoopUVCL,
                        TauLoopUVCL, FlowerModelUVCL]
        return list()
