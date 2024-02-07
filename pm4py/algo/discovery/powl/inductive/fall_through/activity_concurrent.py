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

from collections import Counter
from multiprocessing import Pool, Manager
from typing import Optional, Tuple, List, Any, Dict

from pm4py.algo.discovery.inductive.fall_through.activity_concurrent import ActivityConcurrentUVCL
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.objects.powl.obj import StrictPartialOrder


class POWLActivityConcurrentUVCL(ActivityConcurrentUVCL):

    @classmethod
    def apply(cls, obj: IMDataStructureUVCL, pool: Pool = None, manager: Manager = None,
              parameters: Optional[Dict[str, Any]] = None) -> Optional[
        Tuple[StrictPartialOrder, List[IMDataStructureUVCL]]]:
        candidate = cls._get_candidate(obj, pool, manager, parameters)
        if candidate is None:
            return None
        log = obj.data_structure
        l_a = Counter()
        l_other = Counter()
        for t in log:
            l_a.update({tuple(filter(lambda e: e == candidate, t)): log[t]})
            l_other.update({tuple(filter(lambda e: e != candidate, t)): log[t]})
        children = [IMDataStructureUVCL(l_a), IMDataStructureUVCL(l_other)]
        return StrictPartialOrder(children), children
