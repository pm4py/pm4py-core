from abc import ABC
from typing import Generic

from pm4py.algo.discovery.inductive.base_case.abc import BaseCase, T
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG
from pm4py.objects.process_tree.obj import ProcessTree


class EmptyLogBaseCase(BaseCase[T], ABC, Generic[T]):

    @classmethod
    def leaf(cls, obj=T) -> ProcessTree:
        return ProcessTree()


class EmptyLogBaseCaseUVCL(EmptyLogBaseCase[IMDataStructureUVCL]):

    @classmethod
    def holds(cls, obj=IMDataStructureUVCL) -> bool:
        return len(obj.data_structure) == 0


class EmptyLogBaseCaseDFG(EmptyLogBaseCase[IMDataStructureDFG]):

    @classmethod
    def holds(cls, obj=IMDataStructureDFG):
        dfg = obj.dfg
        return len(dfg.graph) == 0 and len(dfg.start_activities) == 0 and len(dfg.end_activities) == 0
