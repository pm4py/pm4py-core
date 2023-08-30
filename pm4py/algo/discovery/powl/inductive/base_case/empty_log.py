from abc import ABC
from typing import Generic, Optional, Dict, Any

from pm4py.algo.discovery.powl.inductive.base_case.abc import BaseCase, T
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.objects.powl.obj import SilentTransition


class EmptyLogBaseCase(BaseCase[T], ABC, Generic[T]):

    @classmethod
    def leaf(cls, obj=T, parameters: Optional[Dict[str, Any]] = None) -> SilentTransition:
        return SilentTransition()


class EmptyLogBaseCaseUVCL(EmptyLogBaseCase[IMDataStructureUVCL]):

    @classmethod
    def holds(cls, obj=IMDataStructureUVCL, parameters: Optional[Dict[str, Any]] = None) -> bool:
        return len(obj.data_structure) == 0

