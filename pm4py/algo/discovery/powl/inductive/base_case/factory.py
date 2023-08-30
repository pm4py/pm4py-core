from typing import TypeVar, Optional, Dict, Any, Type

from pm4py.algo.discovery.powl.inductive.base_case.abc import BaseCase
from pm4py.algo.discovery.powl.inductive.base_case.empty_log import EmptyLogBaseCaseUVCL
from pm4py.algo.discovery.powl.inductive.base_case.single_activity import SingleActivityBaseCaseUVCL
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure, IMDataStructureUVCL

from pm4py.objects.powl.obj import POWL

T = TypeVar('T', bound=IMDataStructure)
S = TypeVar('S', bound=BaseCase)


class BaseCaseFactory:

    @classmethod
    def get_base_cases(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> list[Type[S]]:
        if type(obj) is IMDataStructureUVCL:
            return [EmptyLogBaseCaseUVCL, SingleActivityBaseCaseUVCL]
        return []

    @classmethod
    def apply_base_cases(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[POWL]:
        for b in BaseCaseFactory.get_base_cases(obj):
            r = b.apply(obj, parameters)
            if r is not None:
                return r
        return None
