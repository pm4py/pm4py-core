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

from multiprocessing import Pool, Manager
from typing import List, TypeVar, Tuple, Optional, Dict, Any, Type

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure, IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.algo.discovery.powl.inductive.fall_through.activity_concurrent import POWLActivityConcurrentUVCL
from pm4py.algo.discovery.powl.inductive.fall_through.activity_once_per_trace import POWLActivityOncePerTraceUVCL
from pm4py.algo.discovery.powl.inductive.fall_through.empty_traces import POWLEmptyTracesUVCL
from pm4py.algo.discovery.powl.inductive.fall_through.flower import POWLFlowerModelUVCL
from pm4py.algo.discovery.powl.inductive.fall_through.strict_tau_loop import POWLStrictTauLoopUVCL
from pm4py.algo.discovery.powl.inductive.fall_through.tau_loop import POWLTauLoopUVCL
from pm4py.objects.powl.obj import POWL

T = TypeVar('T', bound=IMDataStructure)
S = TypeVar('S', bound=FallThrough)


class FallThroughFactory:

    @classmethod
    def get_fall_throughs(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> List[Type[S]]:
        if type(obj) is IMDataStructureUVCL:
            return [POWLEmptyTracesUVCL, POWLActivityOncePerTraceUVCL, POWLActivityConcurrentUVCL,
                    POWLStrictTauLoopUVCL, POWLTauLoopUVCL, POWLFlowerModelUVCL]
        return list()

    @classmethod
    def fall_through(cls, obj: T, pool: Pool, manager: Manager, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[POWL, List[T]]]:
        for f in FallThroughFactory.get_fall_throughs(obj):
            r = f.apply(obj, pool, manager, parameters)
            if r is not None:
                return r
        return None
