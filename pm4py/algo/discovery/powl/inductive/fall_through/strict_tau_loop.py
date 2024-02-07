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
from typing import Optional, Tuple, List, Dict, Any

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.strict_tau_loop import StrictTauLoopUVCL
from pm4py.objects.powl.obj import OperatorPOWL
from pm4py.objects.process_tree.obj import Operator


class POWLStrictTauLoopUVCL(StrictTauLoopUVCL):

    @classmethod
    def apply(cls, obj: IMDataStructureUVCL, pool: Pool = None, manager: Manager = None, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[OperatorPOWL, List[IMDataStructureUVCL]]]:
        log = obj.data_structure
        proj = cls._get_projected_log(log)
        if sum(proj.values()) > sum(log.values()):
            children = [IMDataStructureUVCL(proj), IMDataStructureUVCL(Counter())]
            return OperatorPOWL(Operator.LOOP, children), children

