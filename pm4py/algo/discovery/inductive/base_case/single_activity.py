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
from pm4py.algo.discovery.inductive.base_case.abc import BaseCase
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG
from pm4py.objects.process_tree.obj import ProcessTree
from typing import Optional, Dict, Any


class SingleActivityBaseCaseUVCL(BaseCase[IMDataStructureUVCL]):
    @classmethod
    def holds(cls, obj=IMDataStructureUVCL, parameters: Optional[Dict[str, Any]] = None) -> bool:
        if len(obj.data_structure.keys()) != 1:
            return False
        if len(list(obj.data_structure.keys())[0]) > 1:
            return False
        return True

    @classmethod
    def leaf(cls, obj=IMDataStructureUVCL, parameters: Optional[Dict[str, Any]] = None) -> ProcessTree:
        for t in obj.data_structure:
            if t:
                return ProcessTree(label=t[0])
            else:
                return ProcessTree()


class SingleActivityBaseCaseDFG(BaseCase[IMDataStructureDFG]):

    @classmethod
    def holds(cls, obj=IMDataStructureDFG, parameters: Optional[Dict[str, Any]] = None) -> bool:
        return len(obj.dfg.graph) == 0 and len(set(obj.dfg.start_activities).union(obj.dfg.end_activities)) == 1

    @classmethod
    def leaf(cls, obj=IMDataStructureDFG, parameters: Optional[Dict[str, Any]] = None) -> ProcessTree:
        return ProcessTree(label=list(obj.dfg.start_activities)[0])
