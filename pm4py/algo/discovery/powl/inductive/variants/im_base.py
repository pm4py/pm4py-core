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

from itertools import combinations
from typing import Optional, Tuple, List, TypeVar, Generic, Dict, Any

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.powl.inductive.fall_through.empty_traces import POWLEmptyTracesUVCL
from pm4py.algo.discovery.inductive.variants.abc import InductiveMinerFramework

from pm4py.algo.discovery.powl.inductive.base_case.factory import BaseCaseFactory
from pm4py.algo.discovery.powl.inductive.cuts.factory import CutFactory
from pm4py.algo.discovery.powl.inductive.fall_through.factory import FallThroughFactory
from pm4py.algo.discovery.powl.inductive.variants.powl_discovery_variants import POWLDiscoveryVariant

from pm4py.objects.powl.obj import POWL, StrictPartialOrder, Sequence

T = TypeVar('T', bound=IMDataStructureUVCL)


class IMBasePOWL(Generic[T], InductiveMinerFramework[T]):

    def instance(self) -> POWLDiscoveryVariant:
        return POWLDiscoveryVariant.IM_BASE
    def apply(self, obj: IMDataStructureUVCL, parameters: Optional[Dict[str, Any]] = None) -> POWL:
        empty_traces = POWLEmptyTracesUVCL.apply(obj, parameters)
        if empty_traces is not None:
            return self._recurse(empty_traces[0], empty_traces[1], parameters)
        powl = self.apply_base_cases(obj, parameters)
        if powl is None:
            cut = self.find_cut(obj, parameters)
            if cut is not None:
                powl = self._recurse(cut[0], cut[1], parameters=parameters)
        if powl is None:
            ft = self.fall_through(obj, parameters)
            powl = self._recurse(ft[0], ft[1], parameters=parameters)
        return powl

    def apply_base_cases(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[POWL]:
        return BaseCaseFactory.apply_base_cases(obj, parameters=parameters)

    def find_cut(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[POWL, List[T]]]:
        return CutFactory.find_cut(obj, parameters=parameters)

    def fall_through(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Tuple[POWL, List[T]]:
        return FallThroughFactory.fall_through(obj, self._pool, self._manager, parameters=parameters)

    def _recurse(self, powl: POWL, objs: List[T], parameters: Optional[Dict[str, Any]] = None):
        children = [self.apply(obj, parameters=parameters) for obj in objs]
        if isinstance(powl, StrictPartialOrder):
            if isinstance(powl, Sequence):
                return Sequence(children)
            powl_new = StrictPartialOrder(children)
            for i, j in combinations(range(len(powl.children)), 2):
                if powl.order.is_edge_id(i, j):
                    powl_new.order.add_edge(children[i], children[j])
                elif powl.order.is_edge_id(j, i):
                    powl_new.order.add_edge(children[j], children[i])
            return powl_new
        else:
            powl.children.extend(children)
            return powl

