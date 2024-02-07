from abc import ABC
from typing import Optional, Any, Dict, Generic, Tuple, List

from pm4py.algo.discovery.inductive.cuts.xor import ExclusiveChoiceCut, ExclusiveChoiceCutUVCL, T
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.objects.powl.obj import OperatorPOWL, POWL
from pm4py.objects.process_tree.obj import Operator


class POWLExclusiveChoiceCut(ExclusiveChoiceCut, ABC, Generic[T]):

    @classmethod
    def operator(cls, parameters: Optional[Dict[str, Any]] = None) -> OperatorPOWL:
        raise Exception("This function should not be called!")

    @classmethod
    def apply(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[POWL, List[T]]]:
        g = cls.holds(obj, parameters)
        if g is None:
            return g
        else:
            children = cls.project(obj, g, parameters)
            return OperatorPOWL(Operator.XOR, children), children


class POWLExclusiveChoiceCutUVCL(ExclusiveChoiceCutUVCL, POWLExclusiveChoiceCut[IMDataStructureUVCL], ABC):
    pass
