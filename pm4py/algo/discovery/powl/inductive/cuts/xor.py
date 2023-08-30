from abc import ABC
from typing import Optional, Any, Dict, Generic

from pm4py.algo.discovery.inductive.cuts.xor import ExclusiveChoiceCut, ExclusiveChoiceCutUVCL, T
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.objects.powl.obj import OperatorPOWL
from pm4py.objects.process_tree.obj import Operator


class POWLExclusiveChoiceCut(ExclusiveChoiceCut, ABC, Generic[T]):

    @classmethod
    def operator(cls, parameters: Optional[Dict[str, Any]] = None) -> OperatorPOWL:
        return OperatorPOWL(Operator.XOR, [])


class POWLExclusiveChoiceCutUVCL(ExclusiveChoiceCutUVCL, POWLExclusiveChoiceCut[IMDataStructureUVCL], ABC):
    pass
