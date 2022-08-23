from typing import TypeVar, Generic

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureLog
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTracesUVCL
from pm4py.algo.discovery.inductive.variants.abc import InductiveMinerFramework
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.process_tree.obj import ProcessTree

T = TypeVar('T', bound=IMDataStructureLog)


class IM(Generic[T], InductiveMinerFramework[T]):

    def instance(self) -> IMInstance:
        return IMInstance.IM


class IMUVCL(IM[IMDataStructureUVCL]):
    def apply(self, obj: IMDataStructureUVCL) -> ProcessTree:
        empty_traces = EmptyTracesUVCL.apply(obj)
        if empty_traces is not None:
            return self._recurse(empty_traces[0], empty_traces[1])
        return super().apply(obj)
