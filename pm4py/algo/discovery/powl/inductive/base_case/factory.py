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
from typing import TypeVar, Optional, Dict, Any, Type, List as TList

from pm4py.algo.discovery.powl.inductive.base_case.abc import BaseCase
from pm4py.algo.discovery.powl.inductive.base_case.empty_log import EmptyLogBaseCaseUVCL
from pm4py.algo.discovery.powl.inductive.base_case.single_activity import SingleActivityBaseCaseUVCL
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure, IMDataStructureUVCL

from pm4py.objects.powl.obj import POWL

T = TypeVar('T', bound=IMDataStructure)
S = TypeVar('S', bound=BaseCase)


class BaseCaseFactory:

    @classmethod
    def get_base_cases(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> TList[Type[S]]:
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
