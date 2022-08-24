from typing import List, TypeVar

from pm4py.algo.discovery.inductive.base_case.abc import BaseCase
from pm4py.algo.discovery.inductive.base_case.empty_log import EmptyLogBaseCaseUVCL, EmptyLogBaseCaseDFG
from pm4py.algo.discovery.inductive.base_case.single_activity import SingleActivityBaseCaseUVCL, \
    SingleActivityBaseCaseDFG
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure, IMDataStructureUVCL, IMDataStructureDFG
from pm4py.algo.discovery.inductive.variants.instances import IMInstance

T = TypeVar('T', bound=IMDataStructure)
S = TypeVar('S', bound=BaseCase)


class BaseCaseFactory:

    @classmethod
    def get_base_cases(cls, obj: T, inst: IMInstance) -> List[S]:
        if inst is IMInstance.IM:
            if type(obj) is IMDataStructureUVCL:
                return [EmptyLogBaseCaseUVCL, SingleActivityBaseCaseUVCL]
        if inst is IMInstance.IMD:
            if type(obj) is IMDataStructureDFG:
                return [EmptyLogBaseCaseDFG, SingleActivityBaseCaseDFG]
        return []
