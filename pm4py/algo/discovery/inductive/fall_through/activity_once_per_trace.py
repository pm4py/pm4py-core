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
import copy
from typing import Any, Optional, Dict

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.activity_concurrent import ActivityConcurrentUVCL
from pm4py.util.compression import util as comut


class ActivityOncePerTraceUVCL(ActivityConcurrentUVCL):

    @classmethod
    def _get_candidate(cls, obj: IMDataStructureUVCL, pool=None, manager=None, parameters: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        candidates = sorted(list(comut.get_alphabet(obj.data_structure)))
        for t in obj.data_structure:
            cc = [x for x in candidates]
            for candi in cc:
                if len(list(filter(lambda e: e == candi, t))) != 1:
                    candidates.remove(candi)
            if len(candidates) == 0:
                return None
        return next(iter(candidates))
