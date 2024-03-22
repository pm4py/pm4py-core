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
from typing import Tuple, List, Optional, Dict, Any

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG
from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.objects.dfg.obj import DFG
from pm4py.algo.discovery.inductive.dtypes.im_dfg import InductiveDFG
from copy import copy


class EmptyTracesUVCL(FallThrough[IMDataStructureUVCL]):

    @classmethod
    def apply(cls, obj: IMDataStructureUVCL, pool=None, manager=None, parameters: Optional[Dict[str, Any]] = None) -> Optional[
        Tuple[ProcessTree, List[IMDataStructureUVCL]]]:
        if cls.holds(obj, parameters):
            data_structure = copy(obj.data_structure)
            del data_structure[()]
            if data_structure:
                return ProcessTree(operator=Operator.XOR), [IMDataStructureUVCL(Counter()),
                                                            IMDataStructureUVCL(data_structure)]
            else:
                return ProcessTree(), []
        else:
            return None

    @classmethod
    def holds(cls, obj: IMDataStructureUVCL, parameters: Optional[Dict[str, Any]] = None) -> bool:
        return len(list(filter(lambda t: len(t) == 0, obj.data_structure))) > 0


class EmptyTracesDFG(FallThrough[IMDataStructureDFG]):
    @classmethod
    def apply(cls, obj: IMDataStructureDFG, pool=None, manager=None, parameters: Optional[Dict[str, Any]] = None) -> Optional[
        Tuple[ProcessTree, List[IMDataStructureDFG]]]:
        if cls.holds(obj, parameters):
            return ProcessTree(operator=Operator.XOR), [IMDataStructureDFG(InductiveDFG(DFG())),
                                                        IMDataStructureDFG(InductiveDFG(obj.data_structure.dfg))]
        return None

    @classmethod
    def holds(cls, obj: IMDataStructureDFG, parameters: Optional[Dict[str, Any]] = None) -> bool:
        return obj.data_structure.skip
