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
from typing import TypeVar, Generic, Dict, Any, Optional

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureLog
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTracesUVCL
from pm4py.algo.discovery.inductive.variants.abc import InductiveMinerFramework
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.process_tree.obj import ProcessTree

T = TypeVar('T', bound=IMDataStructureLog)


class IM(Generic[T], InductiveMinerFramework[T]):

    def instance(self) -> IMInstance:
        return IMInstance.IM


class IMUVCL(IM[IMDataStructureUVCL]):
    def apply(self, obj: IMDataStructureUVCL, parameters: Optional[Dict[str, Any]] = None) -> ProcessTree:
        empty_traces = EmptyTracesUVCL.apply(obj, parameters)
        if empty_traces is not None:
            return self._recurse(empty_traces[0], empty_traces[1], parameters)
        return super().apply(obj, parameters)
