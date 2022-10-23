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
from typing import Optional, Dict, Any

from pm4py.algo.discovery.inductive.fall_through.strict_tau_loop import StrictTauLoopUVCL
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL


class TauLoopUVCL(StrictTauLoopUVCL):

    @classmethod
    def _get_projected_log(cls, log: UVCL, parameters: Optional[Dict[str, Any]] = None) -> UVCL:
        start_activities = comut.get_start_activities(log)
        proj = Counter()
        for t in log:
            x = 0
            for i in range(1, len(t)):
                if t[i] in start_activities:
                    proj.update({t[x:i]: log[t]})
                    x = i
            proj.update({t[x:len(t)]: log[t]})
        return proj
