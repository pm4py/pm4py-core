from abc import ABC
from typing import Any, Optional, Dict, Tuple, List, Generic

from pm4py.algo.discovery.inductive.base_case.abc import T
from pm4py.algo.discovery.inductive.cuts.sequence import SequenceCut, SequenceCutUVCL, StrictSequenceCutUVCL, \
    StrictSequenceCut
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.objects.powl.obj import Sequence


class POWLSequenceCut(SequenceCut, ABC, Generic[T]):

    @classmethod
    def operator(cls, parameters: Optional[Dict[str, Any]] = None) -> Sequence:
        return Sequence([])

    @classmethod
    def apply(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[Sequence, List[T]]]:
        g = cls.holds(obj, parameters)
        if g is None:
            return g
        children = cls.project(obj, g, parameters)
        po = Sequence(children)
        return po, children


class POWLStrictSequenceCut(POWLSequenceCut[T], StrictSequenceCut, ABC):
    pass


class POWLSequenceCutUVCL(SequenceCutUVCL, POWLSequenceCut[IMDataStructureUVCL]):
    pass


class POWLStrictSequenceCutUVCL(StrictSequenceCutUVCL, StrictSequenceCut[IMDataStructureUVCL], POWLSequenceCutUVCL):
    pass
