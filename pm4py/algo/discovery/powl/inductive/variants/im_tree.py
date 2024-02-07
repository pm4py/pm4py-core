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
from pm4py.algo.discovery.powl.inductive.utils.filtering import FILTERING_TYPE, FilteringType, \
    filter_most_frequent_variants, FILTERING_THRESHOLD, filter_most_frequent_variants_with_decreasing_factor, \
    DEFAULT_FILTERING_TYPE
from pm4py.algo.discovery.powl.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant

from pm4py.objects.powl.obj import POWL, StrictPartialOrder, Sequence, OperatorPOWL

T = TypeVar('T', bound=IMDataStructureUVCL)


class IMBasePOWL(Generic[T], InductiveMinerFramework[T]):

    def instance(self) -> POWLDiscoveryVariant:
        return POWLDiscoveryVariant.TREE

    def apply(self, obj: IMDataStructureUVCL, parameters: Optional[Dict[str, Any]] = None) -> POWL:
        if FILTERING_TYPE not in parameters.keys():
            filtering_type = DEFAULT_FILTERING_TYPE
        else:
            filtering_type = parameters[FILTERING_TYPE]
            if filtering_type not in FilteringType:
                raise KeyError("Invalid FILTERING_TYPE: " + str(filtering_type))

        empty_traces = POWLEmptyTracesUVCL.apply(obj, parameters)
        if empty_traces is not None:
            return self._recurse(empty_traces[0], empty_traces[1], parameters)

        powl = self.apply_base_cases(obj, parameters)
        if powl is not None:
            return powl

        cut = self.find_cut(obj, parameters)
        if cut is not None:
            powl = self._recurse(cut[0], cut[1], parameters=parameters)

        if powl is not None:
            return powl
        else:
            if filtering_type is FilteringType.DYNAMIC:
                filtered_log = filter_most_frequent_variants(obj.data_structure)
                if len(filtered_log.data_structure) > 0:
                    return self.apply(filtered_log, parameters=parameters)

            elif filtering_type is FilteringType.DECREASING_FACTOR:
                if FILTERING_THRESHOLD in parameters.keys():
                    t = parameters[FILTERING_THRESHOLD]
                    if isinstance(t, float) and 0 <= t < 1:
                        if t > 0:
                            filtered_log = filter_most_frequent_variants_with_decreasing_factor(obj.data_structure,
                                                                                                decreasing_factor=t)
                            if 0 < len(filtered_log.data_structure) < len(obj.data_structure):
                                return self.apply(filtered_log, parameters=parameters)
                    else:
                        raise KeyError("Invalid filtering threshold!")
            else:
                raise KeyError("Invalid filtering type!")

            ft = self.fall_through(obj, parameters)
            return self._recurse(ft[0], ft[1], parameters=parameters)

    def apply_base_cases(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[POWL]:
        return BaseCaseFactory.apply_base_cases(obj, parameters=parameters)

    def find_cut(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[POWL, List[T]]]:
        return CutFactory.find_cut(obj, parameters=parameters)

    def fall_through(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Tuple[POWL, List[T]]:
        return FallThroughFactory.fall_through(obj, self._pool, self._manager, parameters=parameters)

    def _recurse(self, powl: POWL, objs: List[T], parameters: Optional[Dict[str, Any]] = None):
        children = [self.apply(obj, parameters=parameters) for obj in objs]
        if isinstance(powl, StrictPartialOrder):
            powl_new = StrictPartialOrder(children)
            for i, j in combinations(range(len(powl.children)), 2):
                if powl.order.is_edge_id(i, j):
                    powl_new.order.add_edge(children[i], children[j])
                elif powl.order.is_edge_id(j, i):
                    powl_new.order.add_edge(children[j], children[i])
            return powl_new
        else:
            new_powl = OperatorPOWL(operator=powl.operator, children=children)
            return new_powl
