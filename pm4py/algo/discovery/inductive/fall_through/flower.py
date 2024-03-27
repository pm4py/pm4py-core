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

from typing import Optional, Tuple, List, Dict, Any

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG
from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTracesUVCL
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL
from pm4py.objects.dfg.obj import DFG
from pm4py.algo.discovery.inductive.dtypes.im_dfg import InductiveDFG


class FlowerModelUVCL(FallThrough[IMDataStructureUVCL]):

    @classmethod
    def holds(cls, obj: IMDataStructureUVCL, parameters: Optional[Dict[str, Any]] = None) -> bool:
        return not EmptyTracesUVCL.holds(obj, parameters)

    @classmethod
    def apply(cls, obj: IMDataStructureUVCL, pool=None, manager=None, parameters: Optional[Dict[str, Any]] = None) -> Optional[
        Tuple[ProcessTree, List[IMDataStructureUVCL]]]:
        log = obj.data_structure
        uvcl_do = UVCL()
        for a in sorted(list(comut.get_alphabet(log))):
            uvcl_do[(a,)] = 1
        uvcl_redo = UVCL()
        im_uvcl_do = IMDataStructureUVCL(uvcl_do)
        im_uvcl_redo = IMDataStructureUVCL(uvcl_redo)
        return ProcessTree(operator=Operator.LOOP), [im_uvcl_do, im_uvcl_redo]


class FlowerModelDFG(FallThrough[IMDataStructureDFG]):
    @classmethod
    def holds(cls, obj: IMDataStructureDFG, parameters: Optional[Dict[str, Any]] = None) -> bool:
        return True

    @classmethod
    def apply(cls, obj: IMDataStructureDFG, pool=None, manager=None, parameters: Optional[Dict[str, Any]] = None) -> Optional[
        Tuple[ProcessTree, List[IMDataStructureDFG]]]:
        activities = set(obj.dfg.start_activities).union(set(obj.dfg.end_activities)).union(set(x[0] for x in obj.dfg.graph)).union(set(x[1] for x in obj.dfg.graph))
        dfg_do = DFG()
        for a in activities:
            dfg_do.start_activities[a] = 1
            dfg_do.end_activities[a] = 1
        dfg_redo = DFG()
        im_dfg_do = IMDataStructureDFG(InductiveDFG(dfg_do))
        im_dfg_redo = IMDataStructureDFG(InductiveDFG(dfg_redo))
        return ProcessTree(operator=Operator.LOOP), [im_dfg_do, im_dfg_redo]

