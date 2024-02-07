from abc import ABC
from typing import Any, Optional, Dict, Generic, Tuple, List

from pm4py.algo.discovery.inductive.cuts.concurrency import ConcurrencyCut, ConcurrencyCutUVCL, T
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.objects.powl.obj import StrictPartialOrder


class POWLConcurrencyCut(ConcurrencyCut, ABC, Generic[T]):

    @classmethod
    def operator(cls, parameters: Optional[Dict[str, Any]] = None) -> StrictPartialOrder:
        raise Exception("This function should not be called!")

    @classmethod
    def apply(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[StrictPartialOrder, List[T]]]:
        g = cls.holds(obj, parameters)
        if g is None:
            return g
        else:
            children = cls.project(obj, g, parameters)
            return StrictPartialOrder(children), children


class POWLConcurrencyCutUVCL(ConcurrencyCutUVCL, POWLConcurrencyCut[IMDataStructureUVCL]):
    pass

