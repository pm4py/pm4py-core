'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from typing import List, TypeVar, Optional, Dict, Any

from pm4py.algo.discovery.inductive.base_case.abc import BaseCase
from pm4py.algo.discovery.inductive.base_case.empty_log import EmptyLogBaseCaseUVCL, EmptyLogBaseCaseDFG
from pm4py.algo.discovery.inductive.base_case.single_activity import SingleActivityBaseCaseUVCL, \
    SingleActivityBaseCaseDFG
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure, IMDataStructureUVCL, IMDataStructureDFG
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.process_tree.obj import ProcessTree

T = TypeVar('T', bound=IMDataStructure)
S = TypeVar('S', bound=BaseCase)


class BaseCaseFactory:

    @classmethod
    def get_base_cases(cls, obj: T, inst: IMInstance, parameters: Optional[Dict[str, Any]] = None) -> List[S]:
        if inst is IMInstance.IM or inst is IMInstance.IMf:
            if type(obj) is IMDataStructureUVCL:
                return [EmptyLogBaseCaseUVCL, SingleActivityBaseCaseUVCL]
        if inst is IMInstance.IMd:
            if type(obj) is IMDataStructureDFG:
                return [EmptyLogBaseCaseDFG, SingleActivityBaseCaseDFG]
        return []

    @classmethod
    def apply_base_cases(cls, obj: T, inst: IMInstance, parameters: Optional[Dict[str, Any]] = None) -> Optional[ProcessTree]:
        for b in BaseCaseFactory.get_base_cases(obj, inst):
            r = b.apply(obj, parameters)
            if r is not None:
                return r
        return None
