from typing import List

from pm4py.algo.discovery.inductive.base_case.abc import BaseCase
from pm4py.algo.discovery.inductive.base_case.empty_log import EmptyLogBaseCaseUVCL, EmptyLogBaseCaseDFG
from pm4py.algo.discovery.inductive.base_case.single_activity import SingleActivityBaseCaseUVCL, \
    SingleActivityBaseCaseDFG
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure, IMDataStructureUVCL, IMDataStructureDFG
from pm4py.algo.discovery.inductive.variants.instances import IMInstance


class BaseCaseFactory:

    @classmethod
    def get_base_cases(cls, obj: IMDataStructure, inst: IMInstance) -> List[BaseCase]:
        if inst is IMInstance.IM:
            if type(obj) is IMDataStructureUVCL:
                return [EmptyLogBaseCaseUVCL, SingleActivityBaseCaseUVCL]
        if inst is IMInstance.IMD:
            if type(obj) is IMDataStructureDFG:
                return [EmptyLogBaseCaseDFG, SingleActivityBaseCaseDFG]
        return []
